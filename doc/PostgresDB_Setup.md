# ETL and Postgres DB
For the purposes of ETL, it is recommended to use Postgres as this supports PostGIS, a Postgres extension for geographical
information structures. During development the DBMS had to switch from Postgres, to MySQL, to SQLite sure to system restrictions.
If attempting to run this on University of Warwick systems, it is recommeded to perform the ETL process on a separate machine where
it is possible to satisfy the prerequisites, then export the results to use in the modelling process.
### Prerequisites

- A user account with `sudo` privileges.
- No previous installations of Postgres.
- CentOS 7

### Setup Overview
1. Install Postgres version 10 and setup a database.
2. Install PostGIS.
3. Install Python and system requirements.
4. Setup Workspace and provide data.

### 1. Install Postgres version 10 and setup a database

#### 1.1 Install Postgres
Update the CentOS package repositories, for good measure:
```
$ sudo yum update
```
CentOS package repositories contain listings for Postgres packages and libraries, however many of them are outdated,
so the official Postgres repository needs to be used when installing Postgres so that packages resolve to the latest version.

Open the repository configuration file with a text editor such as `nano`:
```
$ sudo nano /etc/yum.repos.d/CentOS-Base.repo
```

This will display the contents of the file. Under the two sections `[base]` and `[updates]` append the line `exclude=postgresql*`. The configuration file should look like this:
```
...
[base]
name=CentOS-$releasever - Base
mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=os&infra=$infra
#baseurl=http://mirror.centos.org/centos/$releasever/os/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7

exclude=postgresql*

#released updates
[updates]
name=CentOS-$releasever - Updates
mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=updates&infra=$infra
#baseurl=http://mirror.centos.org/centos/$releasever/updates/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
exclude=postgresql*
...
```
Exit `nano` using Ctrl-X, then update the package listings:
```
$ sudo yum install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
```
Install Postgres Version 10 and Postgres development libraries:
```
$ sudo yum install postgresql10-server postgresql10-devel
```
Initialise the Postgres database cluster:
```
$ sudo /usr/pgsql-10/bin/postgresql-10-setup initdb
Initializing database ... OK
```
#### 1.2 Configure database authentication
In order for tools such as `osm2pgsql` and `shp2pgsql` to be able to load data into the database, the authentication mechanisms need to allow *local* access without a password.
To do this, open the authentication configuration file with `nano` :
```
$ sudo nano /var/lib/pgsql/10/data/pg_hba.conf
```
Scroll past the comments down to what looks like a table of authentication configuration entries. Under the right-most column `METHOD`, change from `peer` to `trust` for the top 3 entries i.e the local socket connections and local IPv4 and IPv6 connections:
```
...
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust
# IPv4 local connections:
host    all             all             127.0.0.1/32            trust
# IPv6 local connections:
host    all             all             ::1/128                 trust
...
```
Save and close the file. Then, start the Postgres service, and enable Postgres being launched on startup of the system:
```
$ sudo systemctl start postgresql-10
$ sudo systemctl enable postgresql-10
```
If you ever need to change the above (or any other) configuration, you can run `sudo systemctl restart postgresql10.service` to restart Postgres and have the changes take effect.
#### 1.3 Create a database
Switch over to the `postgres` user:
```
$ sudo -i -u postgres 
```
You will know you have successfully switched due to the terminal prompt displaying a different user (or no user at all). Then, create a database making sure to take a note of the database name as this will be required later. In this example, the database name is `tfwm`.
```
postgres@server $ createdb tfwm
```

You can verify that you have created the database by running `psql` and connecting to the created database using `\connect`:

```
postgres@server $ psql
postgres=# \connect tfwm
You are now connected to database "tfwm" as user "postgres".
```

Exit `psql` using `\q` and switch back to your regular using account using `logout`:
```
postgres=# \q
postgres@server $ logout
```
### 2 Install PostGIS

Install the EPEL repository to provide the additional dependencies:
```
$ sudo yum -y install epel-release
```
Install PostGIS version 2.4 for Postgres version 10:
```
$ sudo yum install postgis24_10 postgis24_10-client
```
You can verify the installation of PostGIS by logging in to the Postgres database and creating the PostGIS extension (this will be done automatically for you in the ETL scripts).
```
$ sudo -i -u postgres psql
postgres=# create extension postgis;
CREATE EXTENSION
postgres=# \q
```
### 3 Install Python and system requirements

It is recommened to use a virtualenv for the installation of the requirements. See Python documentation for [setting up a virtualenv](https://docs.python.org/3/tutorial/venv.html) for guidance.
Clone the repository using `git clone`
```
git clone https://github.com/cmconlan/TfWM-Accessibility-Tool.git
```
`cd` to the `src` directory and intstall the requirements with `pip`
```
(venv) $ pip install -r requirements.txt
```
Installing python modules may cause errors due to missing system packages. Refer to the documentation for the python modules
to make sure system prerequisites are met.
If using Postgres for the ETL process, you'll also need the `osm2pgsql` package to load Open Street Map files:
 ```
sudo yum install osm2pgsql
 ```

### 4 Setup workspace and provide data
#### 4.1 Conigure environment variables
The `.env` file under the `src` directory contains system-wide variables used throughout the codebase.
For the purposes of ETL, the following fields need to be filled in:
Note: You may however need to change the DB URL prefix in calls tp `create_connection` to match the database you are using
```
# The absolute path to the top level repository directory e.g /dcs/project/transport-access-tool/TfWM-Accessibility-Tool
ROOT_FOLDER= 
# The path to the location of the .db SQLite file
SQLIE_PATH=
...
```
You may add other variables to the `.env` file, and these can be loaded with `settings.get_environment_variable`
#### 4.2 Provide data files
The file `/config/base/data_files.yaml` lists the data files that you want to upload to the database from `/data`.

- text_dict maps each `.txt` or `.csv` file to a table in the raw schema.
- gis_dict maps each `.shp` file to a table in the `gis` schema.
- osm_file gives the name of the OpenStreetMap `.pbf` file that is uploaded to the `raw schema`.

If you upload any new data sources to the `/data` folder, you also need to add the file (and map it to a corresponding table name, if applicable) to /config/base/data_files.yaml in order for these sources to be added to the database.
