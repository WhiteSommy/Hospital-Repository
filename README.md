## Tech Stack (Dependencies)

### 1. Backend Dependencies
The tech stack will include the following:
 * **virtualenv** as a tool to create isolated Python environments
 * **SQLAlchemy ORM** to be the ORM library of choice
 * **MYSQL** as the database of choice
 * **Python3** and **Flask** as the server language and server framework

```
pip install virtualenv
pip install SQLAlchemy
pip install Flask
```
> **Note** - If I do not mention the specific version of a package, then the default latest stable package will be installed. 

**Initialize and activate a virtualenv using:**
```
python -m virtualenv env
Linux: source env/bin/activate
Windows: source env/Scripts/activate
```
>**Note** - In Windows, the `env` does not have a `bin` directory. Therefore, whoever that wants to activate the venv or virtual env should use the analogous command shown below:
```

```

4. **Install the dependencies:**
```
pip install -r requirements.txt
```

5. **Run the development server:**
```
export FLASK_APP=myapp
export FLASK_ENV=development # enables debug mode
python3 app.py
```
