**EPNM Alarms Application**

This application uses the Evolved Programmable Network Manager (EPNM) Rest API to query unresolved alarm information within the network. These alarm queries can be grouped by location defined groups, or can be individual device specific. The application will present the user with an alarm report in the browser, and the user can download the report to a text-file for future review.

HTML user interface works better in Chrome and Firefox

Contacts:

* Michael Castellana (micastel@cisco.com)
* Steven Yee (steveyee@cisco.com)
* Jason Mah (jamah@cisco.com)
* Santiago Flores (sfloresk@cisco.com)



**Source Installation**

Usually will be something like below:

As this is a Django application you will need to either integrate the application in your production environment or you can
get it operational in a virtual environment on your computer/server. In the distribution is a requirements.txt file that you can
use to get the package requirements that are needed. The requirements file is located in the root directory of the distribution.

It might make sense for you to create a Python Virtual Environment before installing the requirements file. For information on utilizing
a virtual environment please read http://docs.python-guide.org/en/latest/dev/virtualenvs/. Once you have a virtual environment active then
install the packages in the requirements file.

`(virtualenv) % pip install -r requirements.txt
`

To run the the application execute in the root directory of the distribution:
 - python manage.py makemigrations
 - python manage.py migrate
 - python manage.py runserver 0.0.0.0:YOUR_PORT

The root directory also contains a shell script that will perform the three steps above.
To run this script and start the application with one command enter the following in the root directory:
 - ./web_start.sh
This will run the web server and content can be accessed by navigating to localhost:5002/web/ in your browser.

**Known Issues**

Write here limitations or any problem that the app can have.