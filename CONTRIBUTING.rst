How to contribute to Youtool
============================

Thank you for considering to Youtool!

First time setup in your local environment:
-------------------------------------------

- Make sure you have a `GitHub account <https://github.com/>`_

- Fork Youtool to your GitHub account by clicking the `Fork <https://github.com/PythonicCafe/youtool/fork>`_ button

- `Clone <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo#step-2-create-a-local-clone-of-your-fork>`_ your fork locally, replacing your-username in the command below with your actual username

.. code-block::

    git clone https://github.com/your-username/youtool
    cd youtool

Installation Poetry
-------------------
To manage dependencies and packaging for the project, we use Poetry. 
- Please follow the installation instructions provided in the `poetry <https://python-poetry.org/docs/#installation>`_


Setting Up the Virtual Environment
----------------------------------
- After installing Poetry, you need to set up the virtual environment for the project. Navigate to the project directory and run the following command:

.. code-block::

    poetry shell

This command will create and activate a virtual environment for the project.


Installing Dependencies
-----------------------
- Once the virtual environment is activated, you can install the project dependencies by running:

.. code-block::

    poetry install

This command will install all the dependencies listed in the pyproject.toml file.


Creating a Local Branch from a Remote Branch
--------------------------------------------
To start contributing, you need to create a local branch based on a remote branch. 
Use the following commands to achieve this:
1. Fetch the latest changes from the remote repository:

.. code-block::

    git fetch origin

2. Create and switch to a new branch based on the remote branch:

.. code-block::
    
    git checkout -b <new-branch-name> origin/<remote-branch-name>

Push your commits to your fork on GitHub and `create a pull request <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request>`_. Link to the issue being addressed with fixes #123 in the pull request description.

.. code-block::

    git push --set-upstream origin nome-do-seu-branch

Replace <new-branch-name> with your desired branch name and <remote-branch-name> with the name of the remote branch you want to base your work on.

By following these steps, you'll have a local branch set up and ready for your contributions.


Running Tests
-------------
Before submitting your changes, it's important to run the tests to ensure everything is working correctly. 
Depending on whether you are inside or outside the virtual environment, use one of the following commands:

1. Inside the virtual environment:
If you have already activated the virtual environment with poetry shell, run:

.. code-block::
    
    pytest

2. Outside the virtual environment:
If you are not inside the virtual environment, you can still run the tests using Poetry:
    
.. code-block::

    poetry run pytest

By following these steps, you'll ensure that all tests are run correctly before submitting your contributions.

Updating Documentation
----------------------
Our documentation is hosted on Read the Docs, and the configuration files are located in the docs directory. To update the documentation, follow these steps:

1. Navigate to the docs directory:

.. code-block::

    cd docs

2. Make your changes:
    Edit the necessary files to update the documentation. 
    The main configuration file is typically conf.py, but you may also need to update other ``.rst`` files as required.

3. Build the documentation locally:
    After making your changes, you can build the HTML version of the documentation to preview your updates. 
    Run the following command:

.. code-block::

    make html

Open ``_build/html/index.html`` in your browser to view the docs.

Read more about `Sphinx <https://www.sphinx-doc.org/en/master/>`_.
