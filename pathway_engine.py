"""
pathway_engine.py — AI-powered learning roadmap generation using Groq API.
Groq is imported lazily inside functions — never crashes on missing package.
GROQ_API_KEY is read fresh on every call — works even if set after app starts.
"""
import os
import json
import re
from modules.data_manager import get_cached_roadmap, save_roadmap_cache

MODEL = "llama3-8b-8192"

ROADMAP_PROMPT = """You are an expert educational curriculum designer.

Generate a comprehensive, structured learning roadmap for:
- Skill: {skill}
- Starting Level: {level}

Return ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{{
  "skill": "{skill}",
  "level": "{level}",
  "total_duration_weeks": <integer>,
  "description": "<2-sentence overview of this learning path>",
  "phases": [
    {{
      "phase_number": 1,
      "phase_title": "<Phase Title>",
      "duration_weeks": <integer>,
      "objective": "<What the learner will achieve in this phase>",
      "topics": [
        {{
          "id": 1,
          "name": "<Topic Name>",
          "description": "<2-3 sentence explanation of this topic>",
          "estimated_hours": <integer>,
          "key_concepts": ["concept1", "concept2", "concept3"],
          "project_idea": "<A small practical project for this topic>"
        }}
      ]
    }}
  ]
}}

Rules:
- Create 3-5 phases from beginner to advanced
- Each phase must have 3-5 topics
- Topics must be logically ordered (foundations first)
- Be specific and practical for the exact skill requested
- total_duration_weeks should be realistic (12-24 weeks for Beginner, 8-14 for Intermediate)
- Return ONLY the JSON object. Absolutely no text before or after."""


# ─── Static fallback roadmaps (covers all 8 skills) ─────────────────────────

FALLBACK_ROADMAPS = {
    "Python|Beginner": {
        "skill":"Python","level":"Beginner","total_duration_weeks":16,
        "description":"A comprehensive Python journey from zero to job-ready. Covers core syntax, data structures, OOP, and practical projects.",
        "phases":[
            {"phase_number":1,"phase_title":"Python Foundations","duration_weeks":3,"objective":"Understand Python syntax, variables, and control flow",
             "topics":[
                {"id":1,"name":"Python Setup & Basics","description":"Install Python, write your first script, learn variables, data types, and basic I/O operations.","estimated_hours":8,"key_concepts":["variables","data types","print()","input()","operators"],"project_idea":"Build a tip calculator"},
                {"id":2,"name":"Control Flow","description":"Master if/elif/else, for loops, while loops, break and continue. Control exactly how your program runs.","estimated_hours":10,"key_concepts":["if/else","for loop","while loop","range()","break/continue"],"project_idea":"Build a number guessing game"},
                {"id":3,"name":"Functions","description":"Write reusable code with functions. Understand parameters, return values, scope, and lambda expressions.","estimated_hours":10,"key_concepts":["def","return","parameters","scope","lambda","default args"],"project_idea":"Create a unit converter library"},
            ]},
            {"phase_number":2,"phase_title":"Data Structures","duration_weeks":4,"objective":"Work confidently with Python's built-in data structures",
             "topics":[
                {"id":4,"name":"Lists & Tuples","description":"Create and manipulate sequences. Master indexing, slicing, list comprehensions, and common methods.","estimated_hours":10,"key_concepts":["indexing","slicing","list methods","comprehensions","tuples"],"project_idea":"Build a to-do list manager"},
                {"id":5,"name":"Dictionaries & Sets","description":"Use dictionaries for key-value storage and sets for unique collections. Understand hashing.","estimated_hours":8,"key_concepts":["key-value pairs","dict methods","set operations","get()","items()"],"project_idea":"Build a word frequency counter"},
                {"id":6,"name":"File Handling & Exceptions","description":"Read and write files, handle CSV and JSON data. Implement try/except for robust error handling.","estimated_hours":10,"key_concepts":["open()","read/write","try/except","json module","csv module"],"project_idea":"Build a contact book saved to a JSON file"},
            ]},
            {"phase_number":3,"phase_title":"Object-Oriented Programming","duration_weeks":4,"objective":"Design and implement object-oriented programs",
             "topics":[
                {"id":7,"name":"Classes & Objects","description":"Define classes, create objects, use __init__, and understand instance vs class attributes.","estimated_hours":12,"key_concepts":["class","__init__","self","attributes","methods","encapsulation"],"project_idea":"Model a bank account system"},
                {"id":8,"name":"Inheritance & Polymorphism","description":"Extend classes with inheritance, override methods, use super(), understand polymorphism.","estimated_hours":10,"key_concepts":["inheritance","super()","method overriding","polymorphism","ABC"],"project_idea":"Build a simple RPG character system"},
                {"id":9,"name":"Modules & Packages","description":"Organise code into modules, create packages, use pip, and work with the Python standard library.","estimated_hours":8,"key_concepts":["import","modules","packages","pip","__name__","virtualenv"],"project_idea":"Create a reusable utilities package"},
            ]},
            {"phase_number":4,"phase_title":"Practical Python","duration_weeks":5,"objective":"Build real-world applications with Python",
             "topics":[
                {"id":10,"name":"Working with APIs","description":"Make HTTP requests using the requests library, parse JSON responses, and interact with REST APIs.","estimated_hours":12,"key_concepts":["requests","GET/POST","JSON","API keys","status codes"],"project_idea":"Build a weather app using OpenWeatherMap API"},
                {"id":11,"name":"Data Analysis with Pandas","description":"Load, clean, and analyse datasets with Pandas. Perform grouping, aggregation, and basic statistics.","estimated_hours":14,"key_concepts":["DataFrame","Series","groupby","merge","describe()","iloc/loc"],"project_idea":"Analyse a dataset and extract business insights"},
                {"id":12,"name":"Automation & Scripting","description":"Automate repetitive tasks: file management, web scraping, and scheduling scripts.","estimated_hours":12,"key_concepts":["os module","shutil","BeautifulSoup","pathlib","schedule"],"project_idea":"Build an automated file organiser"},
            ]},
        ]
    },
    "Machine Learning|Beginner": {
        "skill":"Machine Learning","level":"Beginner","total_duration_weeks":18,
        "description":"Start from zero and build real ML models. Covers math foundations, core algorithms, and hands-on projects with scikit-learn.",
        "phases":[
            {"phase_number":1,"phase_title":"Math & Python Foundations","duration_weeks":4,"objective":"Build the mathematical and coding foundation for ML",
             "topics":[
                {"id":1,"name":"Python for ML","description":"Learn NumPy, Pandas and Matplotlib — the core tools every ML engineer uses daily.","estimated_hours":12,"key_concepts":["NumPy arrays","Pandas DataFrames","Matplotlib","data loading","EDA"],"project_idea":"Explore and visualise the Titanic dataset"},
                {"id":2,"name":"Statistics & Probability","description":"Understand mean, median, variance, distributions, and Bayes theorem — the backbone of ML.","estimated_hours":10,"key_concepts":["mean/variance","normal distribution","Bayes theorem","correlation","hypothesis testing"],"project_idea":"Statistical analysis of a real dataset"},
                {"id":3,"name":"Linear Algebra Basics","description":"Vectors, matrices, matrix multiplication and eigenvalues — how ML models compute internally.","estimated_hours":8,"key_concepts":["vectors","matrices","dot product","matrix multiply","eigenvalues"],"project_idea":"Implement matrix operations from scratch"},
            ]},
            {"phase_number":2,"phase_title":"Supervised Learning","duration_weeks":5,"objective":"Train models that learn from labelled data",
             "topics":[
                {"id":4,"name":"Linear & Logistic Regression","description":"The building blocks of ML. Predict continuous and binary outcomes, understand loss functions and gradient descent.","estimated_hours":14,"key_concepts":["regression","classification","loss function","gradient descent","MSE","sigmoid"],"project_idea":"Predict house prices with linear regression"},
                {"id":5,"name":"Decision Trees & Random Forests","description":"Tree-based models that are easy to interpret and powerful in practice.","estimated_hours":12,"key_concepts":["decision tree","random forest","Gini impurity","feature importance","bagging"],"project_idea":"Classify iris flowers with a decision tree"},
                {"id":6,"name":"Model Evaluation","description":"Learn cross-validation, confusion matrix, precision/recall, F1-score and ROC-AUC.","estimated_hours":10,"key_concepts":["train/test split","cross-validation","confusion matrix","precision","recall","F1","ROC"],"project_idea":"Compare multiple models on a classification task"},
            ]},
            {"phase_number":3,"phase_title":"Unsupervised & Advanced","duration_weeks":5,"objective":"Work with unlabelled data and improve model performance",
             "topics":[
                {"id":7,"name":"Clustering & Dimensionality Reduction","description":"K-Means, DBSCAN, PCA — group data without labels and reduce complexity.","estimated_hours":12,"key_concepts":["K-Means","DBSCAN","PCA","t-SNE","silhouette score"],"project_idea":"Segment customers with K-Means clustering"},
                {"id":8,"name":"Feature Engineering","description":"The most impactful skill in ML. Create and select the best features for your models.","estimated_hours":10,"key_concepts":["feature selection","encoding","scaling","imputation","polynomial features"],"project_idea":"Engineer features to improve a competition dataset"},
                {"id":9,"name":"Hyperparameter Tuning & Pipelines","description":"Automate model optimisation with GridSearch, RandomSearch, and build production-ready ML pipelines.","estimated_hours":12,"key_concepts":["GridSearchCV","RandomizedSearch","Pipeline","ColumnTransformer","joblib"],"project_idea":"Build an end-to-end ML pipeline for a real problem"},
            ]},
            {"phase_number":4,"phase_title":"Real Projects & Deployment","duration_weeks":4,"objective":"Build and deploy ML projects that work in the real world",
             "topics":[
                {"id":10,"name":"Intro to Neural Networks","description":"Understand perceptrons, backpropagation, and build your first neural network with scikit-learn or Keras.","estimated_hours":14,"key_concepts":["perceptron","layers","activation","backpropagation","Keras","epochs"],"project_idea":"Build a digit recogniser with a neural network"},
                {"id":11,"name":"Kaggle & Real Competitions","description":"Apply everything on Kaggle. Learn the competition workflow from EDA to submission.","estimated_hours":12,"key_concepts":["EDA","feature engineering","ensembling","leaderboard","submission"],"project_idea":"Complete a beginner Kaggle competition end-to-end"},
                {"id":12,"name":"Model Deployment","description":"Serve your ML model as a REST API with Flask/FastAPI and deploy it to the cloud.","estimated_hours":10,"key_concepts":["Flask","FastAPI","pickle","joblib","Docker basics","cloud deploy"],"project_idea":"Deploy a sentiment analyser as a web API"},
            ]},
        ]
    },
    "Data Science|Beginner": {
        "skill":"Data Science","level":"Beginner","total_duration_weeks":16,
        "description":"A practical data science curriculum from data wrangling to storytelling. You will work with real datasets throughout.",
        "phases":[
            {"phase_number":1,"phase_title":"Data Wrangling","duration_weeks":4,"objective":"Load, clean, and prepare any dataset confidently",
             "topics":[
                {"id":1,"name":"Python & Pandas Essentials","description":"Master Pandas for loading, filtering, and transforming tabular data — the daily work of a data scientist.","estimated_hours":12,"key_concepts":["DataFrame","read_csv","filter","groupby","merge","apply"],"project_idea":"Clean and summarise a messy open dataset"},
                {"id":2,"name":"NumPy & Array Operations","description":"Fast numerical computing with NumPy arrays. Vectorised operations replace slow Python loops.","estimated_hours":8,"key_concepts":["ndarray","broadcasting","vectorisation","reshape","linspace","random"],"project_idea":"Implement descriptive stats from scratch with NumPy"},
                {"id":3,"name":"Data Cleaning & EDA","description":"Handle missing values, outliers, and duplicates. Exploratory analysis to understand your data before modelling.","estimated_hours":12,"key_concepts":["missing values","outliers","duplicates","describe()","value_counts","correlation"],"project_idea":"Full EDA on a Kaggle dataset with findings report"},
            ]},
            {"phase_number":2,"phase_title":"Visualisation","duration_weeks":3,"objective":"Turn numbers into clear, insightful charts",
             "topics":[
                {"id":4,"name":"Matplotlib & Seaborn","description":"Create publication-quality static charts. Master the most important plot types for data analysis.","estimated_hours":10,"key_concepts":["line chart","bar chart","histogram","heatmap","scatter","pair plot"],"project_idea":"Create a visual story from a dataset in a Jupyter notebook"},
                {"id":5,"name":"Interactive Dashboards with Plotly","description":"Build interactive charts that users can explore. Plotly Express makes this surprisingly simple.","estimated_hours":10,"key_concepts":["plotly.express","scatter_mapbox","animations","sunburst","Dash basics"],"project_idea":"Build an interactive dashboard for COVID-19 data"},
            ]},
            {"phase_number":3,"phase_title":"Statistics & ML","duration_weeks":5,"objective":"Apply statistical thinking and basic ML to real problems",
             "topics":[
                {"id":6,"name":"Statistical Analysis","description":"Hypothesis testing, A/B testing, confidence intervals — make data-driven decisions with statistical rigour.","estimated_hours":12,"key_concepts":["t-test","chi-squared","p-value","confidence intervals","A/B testing","power"],"project_idea":"Design and analyse a mock A/B test"},
                {"id":7,"name":"Regression & Classification","description":"Apply scikit-learn to build predictive models. Evaluate them properly and avoid overfitting.","estimated_hours":14,"key_concepts":["linear regression","logistic regression","cross-validation","confusion matrix","scikit-learn"],"project_idea":"Predict customer churn with logistic regression"},
                {"id":8,"name":"SQL for Data Scientists","description":"Query databases with SQL. Most real data lives in databases, not CSV files.","estimated_hours":10,"key_concepts":["SELECT","JOIN","GROUP BY","subqueries","window functions","CTEs"],"project_idea":"Analyse an e-commerce database with SQL queries"},
            ]},
            {"phase_number":4,"phase_title":"Storytelling & Portfolio","duration_weeks":4,"objective":"Communicate findings and build a professional portfolio",
             "topics":[
                {"id":9,"name":"Data Storytelling","description":"Turn analysis into compelling narratives. The best analysis means nothing if you can't communicate it.","estimated_hours":8,"key_concepts":["narrative structure","choosing the right chart","annotations","colour theory","presentation"],"project_idea":"Present a complete data story to a mock business audience"},
                {"id":10,"name":"Capstone Project","description":"End-to-end data science project: collect data, clean, analyse, model, visualise, and present.","estimated_hours":20,"key_concepts":["project scoping","full pipeline","documentation","GitHub","README"],"project_idea":"Build a complete DS project on a topic you care about"},
            ]},
        ]
    },
    "Web Development|Beginner": {
        "skill":"Web Development","level":"Beginner","total_duration_weeks":20,
        "description":"Build websites from scratch with HTML, CSS, JavaScript, and a backend framework. Ends with deploying a full-stack app.",
        "phases":[
            {"phase_number":1,"phase_title":"HTML & CSS","duration_weeks":4,"objective":"Build and style any webpage from scratch",
             "topics":[
                {"id":1,"name":"HTML Fundamentals","description":"Structure webpages with semantic HTML5 elements. Understand the DOM and build accessible markup.","estimated_hours":10,"key_concepts":["tags","semantic HTML","forms","tables","links","images","accessibility"],"project_idea":"Build a personal portfolio HTML page"},
                {"id":2,"name":"CSS Styling & Layouts","description":"Style pages with CSS. Master Flexbox and Grid for modern responsive layouts.","estimated_hours":14,"key_concepts":["selectors","box model","Flexbox","Grid","media queries","animations"],"project_idea":"Style your portfolio with a full responsive layout"},
            ]},
            {"phase_number":2,"phase_title":"JavaScript","duration_weeks":5,"objective":"Add interactivity and dynamic behaviour to webpages",
             "topics":[
                {"id":3,"name":"JavaScript Fundamentals","description":"Learn JS syntax, data types, functions, closures, and the event loop.","estimated_hours":14,"key_concepts":["variables","functions","closures","async/await","promises","event loop"],"project_idea":"Build an interactive quiz app"},
                {"id":4,"name":"DOM Manipulation","description":"Control the webpage dynamically — update content, respond to clicks, fetch data without refreshing.","estimated_hours":12,"key_concepts":["querySelector","addEventListener","fetch API","JSON","localStorage"],"project_idea":"Build a todo app that saves to localStorage"},
                {"id":5,"name":"ES6+ Modern JavaScript","description":"Write clean modern JS with arrow functions, destructuring, spread, modules, and optional chaining.","estimated_hours":10,"key_concepts":["arrow functions","destructuring","spread","modules","template literals","nullish coalescing"],"project_idea":"Refactor todo app to use ES6 modules"},
            ]},
            {"phase_number":3,"phase_title":"React.js","duration_weeks":5,"objective":"Build fast, component-based interactive UIs with React",
             "topics":[
                {"id":6,"name":"React Fundamentals","description":"Components, JSX, props, and state. Understand the React rendering model and component lifecycle.","estimated_hours":14,"key_concepts":["components","JSX","props","state","hooks","useEffect"],"project_idea":"Convert your todo app to React"},
                {"id":7,"name":"React Router & State Management","description":"Build multi-page React apps with routing. Manage global state with Context API or Zustand.","estimated_hours":12,"key_concepts":["React Router","useContext","Zustand","prop drilling","URL params"],"project_idea":"Build a multi-page e-commerce product listing"},
                {"id":8,"name":"APIs & Async React","description":"Fetch real data from APIs in React. Handle loading states, errors, and caching.","estimated_hours":10,"key_concepts":["useEffect","fetch","axios","loading state","error boundaries","React Query"],"project_idea":"Build a movie search app using TMDB API"},
            ]},
            {"phase_number":4,"phase_title":"Backend & Deployment","duration_weeks":6,"objective":"Build and deploy a full-stack web application",
             "topics":[
                {"id":9,"name":"Node.js & Express","description":"Build REST APIs with Node.js and Express. Understand middleware, routing, and HTTP.","estimated_hours":14,"key_concepts":["Node.js","Express","middleware","REST API","HTTP methods","JSON"],"project_idea":"Build a REST API for your todo app"},
                {"id":10,"name":"Databases & SQL","description":"Store data in PostgreSQL. Learn SQL queries, ORMs (Prisma/Sequelize), and relationships.","estimated_hours":12,"key_concepts":["PostgreSQL","SQL","Prisma","migrations","one-to-many","joins"],"project_idea":"Add a database to your Express API"},
                {"id":11,"name":"Deployment","description":"Deploy your full-stack app to the internet. Vercel for frontend, Railway/Render for backend.","estimated_hours":8,"key_concepts":["Vercel","Railway","environment variables","CI/CD","domain","HTTPS"],"project_idea":"Deploy your full-stack todo app to production"},
            ]},
        ]
    },
    "Artificial Intelligence|Beginner": {
        "skill":"Artificial Intelligence","level":"Beginner","total_duration_weeks":18,
        "description":"A practical AI curriculum from foundations to building AI-powered applications. Covers ML, NLP, computer vision, and LLMs.",
        "phases":[
            {"phase_number":1,"phase_title":"AI Foundations","duration_weeks":4,"objective":"Understand what AI is and how different approaches work",
             "topics":[
                {"id":1,"name":"Intro to AI & History","description":"What is AI, where it came from, and what the key branches are: ML, DL, NLP, CV.","estimated_hours":8,"key_concepts":["AI vs ML vs DL","supervised/unsupervised","neural networks","AI history","current state"],"project_idea":"Research and present 3 real AI applications in a domain you care about"},
                {"id":2,"name":"Python for AI","description":"Get comfortable with NumPy, Pandas, and Matplotlib — the tools every AI practitioner uses.","estimated_hours":12,"key_concepts":["NumPy","Pandas","Matplotlib","Jupyter notebooks","data loading"],"project_idea":"EDA and visualisation of an AI-relevant dataset"},
                {"id":3,"name":"ML with Scikit-learn","description":"Train your first models. Classification, regression, and evaluation with the industry-standard library.","estimated_hours":14,"key_concepts":["scikit-learn","train/test split","cross-validation","accuracy","F1 score"],"project_idea":"Build a spam email classifier"},
            ]},
            {"phase_number":2,"phase_title":"Deep Learning","duration_weeks":5,"objective":"Build and train neural networks for real tasks",
             "topics":[
                {"id":4,"name":"Neural Networks & Backpropagation","description":"How neural nets learn. Understand forward pass, loss, and gradient descent from scratch.","estimated_hours":14,"key_concepts":["perceptron","hidden layers","activation functions","backpropagation","gradient descent","loss"],"project_idea":"Implement a neural network for digit recognition"},
                {"id":5,"name":"CNNs for Computer Vision","description":"Convolutional Neural Networks — the architecture behind image recognition and detection.","estimated_hours":14,"key_concepts":["convolution","pooling","feature maps","transfer learning","ResNet","data augmentation"],"project_idea":"Build an image classifier with transfer learning"},
                {"id":6,"name":"RNNs & Sequence Models","description":"Process sequential data — text, time series — with RNNs and LSTMs.","estimated_hours":12,"key_concepts":["RNN","LSTM","GRU","sequence-to-sequence","time series","vanishing gradient"],"project_idea":"Build a sentiment analyser for movie reviews"},
            ]},
            {"phase_number":3,"phase_title":"NLP & LLMs","duration_weeks":5,"objective":"Work with language models and build text AI applications",
             "topics":[
                {"id":7,"name":"NLP Fundamentals","description":"Text preprocessing, tokenisation, embeddings, and classical NLP with NLTK and spaCy.","estimated_hours":12,"key_concepts":["tokenisation","TF-IDF","word2vec","named entity recognition","sentiment","spaCy"],"project_idea":"Build a text summariser and keyword extractor"},
                {"id":8,"name":"Transformers & Hugging Face","description":"Use pre-trained transformer models for classification, generation, and Q&A with the Hugging Face ecosystem.","estimated_hours":14,"key_concepts":["attention","BERT","GPT","fine-tuning","Hugging Face pipeline","tokenizer"],"project_idea":"Fine-tune BERT for a custom text classification task"},
                {"id":9,"name":"LLMs & Prompt Engineering","description":"Work with large language models via APIs. Master prompt engineering to get reliable, useful outputs.","estimated_hours":10,"key_concepts":["prompt engineering","few-shot","chain-of-thought","RAG","LangChain","Groq API"],"project_idea":"Build an AI tutor chatbot using an LLM API"},
            ]},
            {"phase_number":4,"phase_title":"AI Applications","duration_weeks":4,"objective":"Build complete AI-powered applications and deploy them",
             "topics":[
                {"id":10,"name":"Reinforcement Learning Basics","description":"Agents that learn by trial and error. OpenAI Gym, Q-learning, and policy gradients.","estimated_hours":12,"key_concepts":["agent","environment","reward","Q-learning","policy gradient","OpenAI Gym"],"project_idea":"Train an agent to play CartPole with Q-learning"},
                {"id":11,"name":"AI Ethics & Responsible AI","description":"Bias, fairness, interpretability, and the societal implications of AI systems.","estimated_hours":6,"key_concepts":["bias","fairness","interpretability","SHAP","LIME","AI safety","regulation"],"project_idea":"Audit an ML model for bias and write a fairness report"},
                {"id":12,"name":"Capstone AI Project","description":"Build a complete AI application: pick a problem, collect data, train a model, build a UI, and deploy.","estimated_hours":20,"key_concepts":["project scoping","full pipeline","Streamlit/Gradio","deployment","documentation"],"project_idea":"Build and deploy an AI-powered app in your chosen domain"},
            ]},
        ]
    },
    "DevOps|Beginner": {
        "skill":"DevOps","level":"Beginner","total_duration_weeks":16,
        "description":"From Linux basics to CI/CD pipelines and Kubernetes. A practical DevOps curriculum focused on real tools.",
        "phases":[
            {"phase_number":1,"phase_title":"Linux & Git","duration_weeks":3,"objective":"Master the command line and version control",
             "topics":[
                {"id":1,"name":"Linux Command Line","description":"Navigate the filesystem, manage files, processes, permissions, and write basic shell scripts.","estimated_hours":12,"key_concepts":["bash","ls/cd/mkdir","chmod","grep","pipes","shell scripting","cron"],"project_idea":"Write a shell script that automates a system backup"},
                {"id":2,"name":"Git & Version Control","description":"Track code changes, collaborate with branches, resolve merge conflicts, and use GitHub.","estimated_hours":10,"key_concepts":["init/clone","add/commit","branches","merge","rebase","pull requests","GitHub"],"project_idea":"Manage a project with Git branching strategy"},
                {"id":3,"name":"Networking Basics","description":"IP addresses, DNS, HTTP/HTTPS, TCP/UDP, ports — how computers talk to each other.","estimated_hours":8,"key_concepts":["IP/TCP/UDP","DNS","HTTP","ports","firewalls","SSH","curl"],"project_idea":"Diagnose a network issue using CLI tools"},
            ]},
            {"phase_number":2,"phase_title":"Docker & Containers","duration_weeks":4,"objective":"Containerise applications with Docker",
             "topics":[
                {"id":4,"name":"Docker Fundamentals","description":"Containers vs VMs, images, containers, and the Docker CLI. Run anything anywhere.","estimated_hours":12,"key_concepts":["images","containers","Dockerfile","docker run","volumes","networks"],"project_idea":"Containerise a Python web app with Docker"},
                {"id":5,"name":"Docker Compose","description":"Define and run multi-container applications. App + database + cache in one YAML file.","estimated_hours":10,"key_concepts":["docker-compose.yml","services","depends_on","env vars","health checks"],"project_idea":"Run a full app stack (web + db + redis) with Compose"},
                {"id":6,"name":"Container Registry & Security","description":"Push images to Docker Hub or ECR. Scan for vulnerabilities and apply security best practices.","estimated_hours":8,"key_concepts":["Docker Hub","ECR","image scanning","non-root user","secrets","multi-stage builds"],"project_idea":"Build and push a minimal secure Docker image"},
            ]},
            {"phase_number":3,"phase_title":"CI/CD Pipelines","duration_weeks":4,"objective":"Automate build, test, and deploy workflows",
             "topics":[
                {"id":7,"name":"GitHub Actions","description":"Automate your workflow with GitHub Actions. Build, test, and deploy on every push.","estimated_hours":12,"key_concepts":["workflows","jobs","steps","triggers","secrets","artifacts","matrix builds"],"project_idea":"Build a CI pipeline that tests and lints on every PR"},
                {"id":8,"name":"Infrastructure as Code","description":"Define infrastructure with Terraform. Provision cloud resources reproducibly.","estimated_hours":12,"key_concepts":["Terraform","HCL","providers","state","plan/apply","modules"],"project_idea":"Provision an EC2 instance and S3 bucket with Terraform"},
                {"id":9,"name":"Monitoring & Logging","description":"Observe your systems with Prometheus, Grafana, and ELK. Know what's happening in production.","estimated_hours":10,"key_concepts":["Prometheus","Grafana","ELK stack","alerting","log aggregation","SLIs/SLOs"],"project_idea":"Set up a monitoring dashboard for a Docker app"},
            ]},
            {"phase_number":4,"phase_title":"Kubernetes & Cloud","duration_weeks":5,"objective":"Orchestrate containers at scale in the cloud",
             "topics":[
                {"id":10,"name":"Kubernetes Fundamentals","description":"Pods, deployments, services, and ingress. Orchestrate containers across a cluster.","estimated_hours":16,"key_concepts":["pods","deployments","services","ingress","ConfigMap","secrets","kubectl"],"project_idea":"Deploy a containerised app on a local Kubernetes cluster"},
                {"id":11,"name":"Cloud Platforms (AWS/GCP)","description":"Core cloud services: compute, storage, networking, and managed databases on AWS or GCP.","estimated_hours":12,"key_concepts":["EC2","S3","RDS","VPC","IAM","managed Kubernetes (EKS/GKE)"],"project_idea":"Deploy a Kubernetes app on a managed cloud cluster"},
                {"id":12,"name":"DevOps Capstone","description":"Build a complete DevOps pipeline: containerised app, CI/CD, infrastructure-as-code, and monitoring.","estimated_hours":16,"key_concepts":["full pipeline","GitOps","ArgoCD","blue-green deploy","rollback"],"project_idea":"Full GitOps pipeline for a microservices app"},
            ]},
        ]
    },
    "Cloud Computing|Beginner": {
        "skill":"Cloud Computing","level":"Beginner","total_duration_weeks":14,
        "description":"Start with cloud fundamentals and work up to architecting scalable systems on AWS. Certification-ready content.",
        "phases":[
            {"phase_number":1,"phase_title":"Cloud Fundamentals","duration_weeks":3,"objective":"Understand cloud concepts and core services",
             "topics":[
                {"id":1,"name":"What is Cloud Computing","description":"IaaS vs PaaS vs SaaS, public vs private cloud, regions and availability zones, shared responsibility model.","estimated_hours":8,"key_concepts":["IaaS/PaaS/SaaS","regions","AZs","shared responsibility","pricing models"],"project_idea":"Set up a free-tier AWS account and explore the console"},
                {"id":2,"name":"Compute & Storage","description":"EC2 instances, S3 buckets, and EBS volumes — the core building blocks of any cloud architecture.","estimated_hours":12,"key_concepts":["EC2","instance types","S3","EBS","AMIs","auto-scaling","pricing"],"project_idea":"Host a static website on S3 with CloudFront CDN"},
                {"id":3,"name":"Networking in the Cloud","description":"VPCs, subnets, security groups, load balancers, and Route 53. Build secure cloud networks.","estimated_hours":10,"key_concepts":["VPC","subnets","security groups","NACLs","load balancer","Route 53","NAT gateway"],"project_idea":"Design and deploy a 3-tier VPC architecture"},
            ]},
            {"phase_number":2,"phase_title":"Core Services","duration_weeks":4,"objective":"Use managed cloud services to build real applications",
             "topics":[
                {"id":4,"name":"Databases in the Cloud","description":"RDS for relational, DynamoDB for NoSQL, and ElastiCache for caching. Choose the right database.","estimated_hours":12,"key_concepts":["RDS","DynamoDB","ElastiCache","read replicas","backups","multi-AZ"],"project_idea":"Build a serverless CRUD API with DynamoDB"},
                {"id":5,"name":"Serverless & Lambda","description":"Run code without managing servers. AWS Lambda, API Gateway, and event-driven architecture.","estimated_hours":12,"key_concepts":["Lambda","API Gateway","triggers","cold start","SAM","event-driven"],"project_idea":"Build a serverless image resizer with Lambda and S3"},
                {"id":6,"name":"IAM & Security","description":"Identity, access, and encryption. The most important topic for cloud security and compliance.","estimated_hours":10,"key_concepts":["IAM users/roles","policies","least privilege","MFA","KMS","CloudTrail","GuardDuty"],"project_idea":"Audit and secure an existing AWS environment"},
            ]},
            {"phase_number":3,"phase_title":"Architecture & Operations","duration_weeks":4,"objective":"Design scalable, resilient cloud architectures",
             "topics":[
                {"id":7,"name":"Cloud Architecture Patterns","description":"Well-Architected Framework: reliability, performance, security, cost, and operational excellence.","estimated_hours":12,"key_concepts":["Well-Architected","high availability","disaster recovery","microservices","event-driven"],"project_idea":"Design an architecture for a high-traffic e-commerce site"},
                {"id":8,"name":"Monitoring & Cost Optimisation","description":"CloudWatch, Cost Explorer, and Trusted Advisor. Never get a surprise bill.","estimated_hours":8,"key_concepts":["CloudWatch","alarms","dashboards","Cost Explorer","Savings Plans","rightsizing"],"project_idea":"Set up billing alerts and a cost dashboard"},
                {"id":9,"name":"Certification Prep (AWS CCP)","description":"Prepare for the AWS Cloud Practitioner exam — the entry-level cloud certification.","estimated_hours":16,"key_concepts":["AWS CCP domains","shared responsibility","pricing","support plans","global infrastructure"],"project_idea":"Pass a full-length AWS CCP practice exam with 80%+"},
            ]},
            {"phase_number":4,"phase_title":"Advanced Services","duration_weeks":3,"objective":"Leverage advanced cloud services for modern applications",
             "topics":[
                {"id":10,"name":"Containers on Cloud (ECS/EKS)","description":"Run Docker containers at scale with ECS Fargate or EKS Kubernetes.","estimated_hours":12,"key_concepts":["ECS","Fargate","EKS","task definitions","services","Helm charts"],"project_idea":"Deploy a containerised app on ECS Fargate"},
                {"id":11,"name":"DevOps on Cloud","description":"CodePipeline, CodeBuild, CodeDeploy — a fully managed CI/CD pipeline on AWS.","estimated_hours":10,"key_concepts":["CodePipeline","CodeBuild","CodeDeploy","Blue/Green","CloudFormation"],"project_idea":"Build a full CI/CD pipeline with AWS Code services"},
            ]},
        ]
    },
    "Cybersecurity|Beginner": {
        "skill":"Cybersecurity","level":"Beginner","total_duration_weeks":16,
        "description":"From security fundamentals to ethical hacking and defence. Hands-on with real tools throughout.",
        "phases":[
            {"phase_number":1,"phase_title":"Security Foundations","duration_weeks":3,"objective":"Understand the core concepts of cybersecurity",
             "topics":[
                {"id":1,"name":"Security Fundamentals","description":"CIA Triad, threat actors, attack surfaces, and the security mindset. Why security matters.","estimated_hours":8,"key_concepts":["CIA Triad","threat actors","attack surface","risk","vulnerabilities","defence in depth"],"project_idea":"Create a threat model for a simple web application"},
                {"id":2,"name":"Networking for Security","description":"TCP/IP deep dive, Wireshark packet analysis, DNS, HTTP/HTTPS, and common protocols.","estimated_hours":12,"key_concepts":["TCP/IP","UDP","Wireshark","DNS","HTTP/HTTPS","TLS","ARP","ICMP"],"project_idea":"Capture and analyse network traffic with Wireshark"},
                {"id":3,"name":"Linux for Security","description":"Linux command line with a security focus: file permissions, users, processes, and log analysis.","estimated_hours":10,"key_concepts":["chmod/chown","/etc/passwd","processes","iptables","log files","bash scripting"],"project_idea":"Harden a Linux server using security best practices"},
            ]},
            {"phase_number":2,"phase_title":"Offensive Security","duration_weeks":4,"objective":"Learn how attackers think to defend better",
             "topics":[
                {"id":4,"name":"Ethical Hacking Methodology","description":"Reconnaissance, scanning, exploitation, and post-exploitation — the penetration testing process.","estimated_hours":12,"key_concepts":["OSINT","Nmap","vulnerability scanning","CVEs","Metasploit","Burp Suite"],"project_idea":"Complete a beginner room on TryHackMe or HackTheBox"},
                {"id":5,"name":"Web Application Security","description":"OWASP Top 10 vulnerabilities: SQL injection, XSS, CSRF, and how to exploit and fix them.","estimated_hours":14,"key_concepts":["SQL injection","XSS","CSRF","IDOR","OWASP Top 10","Burp Suite","DVWA"],"project_idea":"Find and exploit OWASP Top 10 vulnerabilities in DVWA"},
                {"id":6,"name":"Cryptography","description":"Symmetric and asymmetric encryption, hashing, PKI, TLS — how data is protected.","estimated_hours":10,"key_concepts":["AES","RSA","hashing","SHA","PKI","TLS/SSL","certificates","key exchange"],"project_idea":"Implement encryption/decryption and crack weak hashes"},
            ]},
            {"phase_number":3,"phase_title":"Defensive Security","duration_weeks":4,"objective":"Build and operate security defences",
             "topics":[
                {"id":7,"name":"Security Operations (SOC)","description":"SIEM tools, log analysis, incident detection, and the analyst workflow in a Security Operations Centre.","estimated_hours":12,"key_concepts":["SIEM","Splunk","ELK","IOCs","alerts","playbooks","triage","MITRE ATT&CK"],"project_idea":"Set up a home SIEM lab and detect simulated attacks"},
                {"id":8,"name":"Incident Response","description":"Detect, contain, eradicate, and recover from security incidents. The IR playbook.","estimated_hours":10,"key_concepts":["PICERL","forensics","memory analysis","disk imaging","chain of custody","reporting"],"project_idea":"Respond to a simulated incident in a CTF environment"},
                {"id":9,"name":"Cloud Security","description":"Securing cloud environments: misconfigurations, IAM issues, and cloud-native security tools.","estimated_hours":10,"key_concepts":["cloud misconfigs","S3 buckets","IAM over-privilege","CloudTrail","GuardDuty","CSPM"],"project_idea":"Audit an AWS environment and find security issues"},
            ]},
            {"phase_number":4,"phase_title":"Career & Certifications","duration_weeks":5,"objective":"Get certified and start your cybersecurity career",
             "topics":[
                {"id":10,"name":"CompTIA Security+ Prep","description":"The most popular entry-level security cert. Covers all domains needed for a security analyst role.","estimated_hours":20,"key_concepts":["Security+ domains","threats","cryptography","PKI","identity","network security"],"project_idea":"Pass a full-length Security+ practice exam with 85%+"},
                {"id":11,"name":"CTF Competitions","description":"Capture The Flag competitions are the best way to sharpen offensive skills. Picoctf, HackTheBox, CTFtime.","estimated_hours":14,"key_concepts":["web","crypto","forensics","reverse engineering","pwn","OSINT"],"project_idea":"Complete 10 CTF challenges across different categories"},
                {"id":12,"name":"Portfolio & Job Hunting","description":"Build a home lab, write-ups, and GitHub portfolio. Apply for security analyst and junior pen tester roles.","estimated_hours":10,"key_concepts":["home lab","write-ups","LinkedIn","resume","bug bounty","interview prep"],"project_idea":"Publish 3 detailed write-ups of CTF challenges on GitHub"},
            ]},
        ]
    },
}

# Add Intermediate/Advanced variants via simple derivation
def _make_intermediate(base):
    import copy
    rm = copy.deepcopy(base)
    rm["level"] = "Intermediate"
    rm["total_duration_weeks"] = max(8, rm["total_duration_weeks"] - 4)
    rm["description"] = rm["description"].replace("from zero", "building on existing knowledge").replace("from scratch", "from intermediate level")
    if rm["phases"]:
        rm["phases"] = rm["phases"][1:]   # skip the foundations phase
        for i, ph in enumerate(rm["phases"], 1):
            ph["phase_number"] = i
    return rm

def _make_advanced(base):
    import copy
    rm = copy.deepcopy(base)
    rm["level"] = "Advanced"
    rm["total_duration_weeks"] = max(6, rm["total_duration_weeks"] - 8)
    rm["description"] = "Advanced-level curriculum focusing on expert techniques, system design, and production-ready patterns."
    if rm["phases"]:
        rm["phases"] = rm["phases"][2:]   # keep only last 2 phases
        for i, ph in enumerate(rm["phases"], 1):
            ph["phase_number"] = i
    if not rm["phases"]:
        rm["phases"] = [base["phases"][-1]]  # at least keep last phase
    return rm

for skill_key in list(FALLBACK_ROADMAPS.keys()):
    if "|Beginner" in skill_key:
        skill = skill_key.replace("|Beginner","")
        if f"{skill}|Intermediate" not in FALLBACK_ROADMAPS:
            FALLBACK_ROADMAPS[f"{skill}|Intermediate"] = _make_intermediate(FALLBACK_ROADMAPS[skill_key])
        if f"{skill}|Advanced" not in FALLBACK_ROADMAPS:
            FALLBACK_ROADMAPS[f"{skill}|Advanced"] = _make_advanced(FALLBACK_ROADMAPS[skill_key])


# ─── Groq API call (lazy import) ──────────────────────────────────────────────

def _call_groq(skill, level):
    """Call Groq API. Returns validated dict or None. All imports are lazy."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from groq import Groq           # lazy import — no crash if not installed
        client = Groq(api_key=api_key)
        prompt = ROADMAP_PROMPT.format(skill=skill, level=level)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4096,
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown fences
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\s*```\s*$", "", raw, flags=re.MULTILINE)
        raw = raw.strip()
        result = json.loads(raw)
        return result if _validate_roadmap(result) else None
    except Exception:
        return None


def _validate_roadmap(roadmap):
    if not isinstance(roadmap, dict):
        return False
    if not all(k in roadmap for k in ["skill", "phases"]):
        return False
    if not isinstance(roadmap["phases"], list) or not roadmap["phases"]:
        return False
    for phase in roadmap["phases"]:
        if not isinstance(phase.get("topics"), list) or not phase["topics"]:
            return False
        for t in phase["topics"]:
            if not t.get("name"):
                return False
    return True


def generate_roadmap(skill, level, force_refresh=False):
    """
    Main entry. Priority order:
    1. Session cache (unless force_refresh)
    2. Disk cache (unless force_refresh)
    3. Groq AI
    4. Static fallback
    5. Generic fallback
    """
    if not force_refresh:
        cached = get_cached_roadmap(skill, level)
        if cached and _validate_roadmap(cached):
            return cached

    roadmap = _call_groq(skill, level)
    if roadmap:
        save_roadmap_cache(skill, level, roadmap)
        return roadmap

    key = f"{skill}|{level}"
    if key in FALLBACK_ROADMAPS:
        return FALLBACK_ROADMAPS[key]

    return _generic_fallback(skill, level)


def _generic_fallback(skill, level):
    duration = {"Beginner": 16, "Intermediate": 12, "Advanced": 8}.get(level, 14)
    return {
        "skill": skill, "level": level,
        "total_duration_weeks": duration,
        "description": f"A structured {level} learning path for {skill}. Complete each phase in order, building on previous knowledge.",
        "phases": [
            {
                "phase_number": 1, "phase_title": f"{skill} Foundations",
                "duration_weeks": duration // 4, "objective": f"Build core {skill} knowledge",
                "topics": [
                    {"id":1,"name":f"Introduction to {skill}","description":f"Get started with {skill}. Understand the basics, set up your environment, and write your first program.","estimated_hours":8,"key_concepts":["fundamentals","setup","first project","core syntax"],"project_idea":f"Hello World and setup project in {skill}"},
                    {"id":2,"name":"Core Concepts","description":f"Deep dive into the fundamental concepts of {skill}.","estimated_hours":12,"key_concepts":["core theory","basic operations","key patterns"],"project_idea":"Build a small working project"},
                    {"id":3,"name":"Practice & Projects","description":"Apply what you've learned in hands-on projects.","estimated_hours":14,"key_concepts":["application","debugging","problem solving"],"project_idea":"Complete a beginner capstone project"},
                ]
            },
            {
                "phase_number": 2, "phase_title": "Intermediate Skills",
                "duration_weeks": duration // 4, "objective": f"Develop intermediate {skill} proficiency",
                "topics": [
                    {"id":4,"name":"Intermediate Patterns","description":f"Intermediate-level patterns and best practices in {skill}.","estimated_hours":12,"key_concepts":["patterns","best practices","design"],"project_idea":"Build a medium-complexity project"},
                    {"id":5,"name":"Working with Real Data","description":"Handle real-world data, APIs, and external integrations.","estimated_hours":10,"key_concepts":["data handling","APIs","integration"],"project_idea":"Connect to a real API or data source"},
                    {"id":6,"name":"Testing & Error Handling","description":"Write robust, tested code with proper error handling.","estimated_hours":8,"key_concepts":["testing","error handling","debugging","logging"],"project_idea":"Add full test coverage to a previous project"},
                ]
            },
            {
                "phase_number": 3, "phase_title": "Advanced & Production",
                "duration_weeks": duration // 2, "objective": f"Master {skill} for production use",
                "topics": [
                    {"id":7,"name":"Advanced Architecture","description":f"Advanced design patterns and architecture for {skill} applications.","estimated_hours":16,"key_concepts":["architecture","scalability","performance","design patterns"],"project_idea":"Architect and build a production-grade project"},
                    {"id":8,"name":"Deployment & Operations","description":"Deploy your project to production and keep it running.","estimated_hours":10,"key_concepts":["deployment","monitoring","CI/CD","cloud"],"project_idea":"Deploy your project to the internet"},
                    {"id":9,"name":"Career Preparation","description":"Prepare for interviews and build your professional portfolio.","estimated_hours":12,"key_concepts":["interview prep","portfolio","open source","networking"],"project_idea":"Publish 3 projects to GitHub with full documentation"},
                ]
            },
        ]
    }


def get_all_topics(roadmap):
    result = []
    for phase in roadmap.get("phases", []):
        for topic in phase.get("topics", []):
            result.append({
                **topic,
                "phase_title":  phase.get("phase_title", ""),
                "phase_number": phase.get("phase_number", 0),
            })
    return result


def get_total_topic_count(roadmap):
    return len(get_all_topics(roadmap))
