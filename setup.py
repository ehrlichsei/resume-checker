from setuptools import setup, find_packages

setup(
    name='resume_analyzer',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask==3.0.0',
        'Flask-SQLAlchemy==3.1.1',
        'Flask-Cors==4.0.0',
        'python-dotenv==1.0.0',
        'openai==1.3.0',
        'stripe==7.10.0',
        'Werkzeug==3.0.1',
        'SQLAlchemy==2.0.23',
        'pytest==7.4.3'
    ]
)
