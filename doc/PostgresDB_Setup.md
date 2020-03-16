# ETL and Postgres DB

### Prerequisites

- A user account with `sudo` privileges.

### Setup Overview
1. Install Postgres version 10 and setup a database.
2. Install PostGIS.
3. Install Python requirements.
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
### 3 Install Python requirements

*To be continued...*