# SourceGraph setup from source (without `sg`)

The following instructions are from our old quickstart guide before we had sg setup guiding new users through the setup process.

## Install dependencies

Sourcegraph has the following dependencies:
- Git (v2.18 or higher)
- Go (see current version in .tool-versions)
- Node JS (see current recommended version in .nvmrc)
- make
- Docker (v18 or higher)
   - For macOS we recommend using Docker for Mac instead of docker-machine
- PostgreSQL (v12 or higher)
- Redis (v5.0.7 or higher)
- Yarn (v1.10.1 or higher)
- SQLite tools
- Comby (v0.11.3 or higher)

Below are instructions to install these dependencies:

- MacOS
   - Optional: asdf for an alternate way of managing dependencies, especially different versions of programming languages.
   - Install Homebrew.
   - Install Docker for Mac.
   - Install Go, Yarn, Git, Comby, SQLite tools, and jq with the following command: `brew install go yarn git gnu-sed comby pcre sqlite jq`
   - Install PostgreSQL and Redis Without Docker: `brew install postgresql` `brew install redis` `brew services start postgresql` `brew services start redis`
      - Ensure psql, the PostgreSQL command line client, is on your $PATH.
   - Install the current recommended version of Node JS by running the following in the sourcegraph/sourcegraph repository clone

- Ubuntu
   - Go: `sudo add-apt-repository ppa:longsleep/golang-backports`
   - Docker: `curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -` `sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"`
   - Yarn: `curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -` `echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list`
   - Update repositories: `sudo apt-get update`
   - Install dependencies: `sudo apt install -y make git-all libpcre3-dev libsqlite3-dev pkg-config golang-go docker-ce docker-ce-cli containerd.io yarn jq libnss3-tools`
   - Install comby: `curl -L https://github.com/comby-tools/comby/releases/download/0.11.3/comby-0.11.3-x86_64-linux.tar.gz | tar xvz` `chmod +x comby-*-linux` `mv comby-*-linux /usr/local/bin/comby`
   - Install current recommendend version of Node JS
   - Run Postgres and Redis manually Without Docker
   - Install PostgreSQL and Redis with the following commands: `sudo apt install -y redis-server` `sudo apt install -y postgresql postgresql-contrib` `sudo systemctl enable --now postgresql` `sudo systemctl enable --now redis-server.service`
   - (optional) asdf: asdf is a CLI tool that manages runtime versions for a number of different languages and tools. It can be likened to a language-agnostic version of nvm or pyenv.

## Get the code

Run the following command in a folder where you want to keep a copy of the code. Command will create a new sub-folder (sourcegraph) in this folder.

```
git clone https://github.com/sourcegraph/sourcegraph.git
```

## Initialize your database

```
# with docker
createdb --host=localhost --user=sourcegraph --owner=sourcegraph --encoding=UTF8 --template=template0 sourcegraph

env:
    PGHOST: localhost
    PGPASSWORD: sourcegraph
    PGUSER: sourcegraph
```

```
# without docker
createdb
createuser --superuser sourcegraph
psql -c "ALTER USER sourcegraph WITH PASSWORD 'sourcegraph';"
createdb --owner=sourcegraph --encoding=UTF8 --template=template0 sourcegraph

env:
  PGPORT=5432
  PGHOST=localhost
  PGUSER=sourcegraph
  PGPASSWORD=sourcegraph
  PGDATABASE=sourcegraph
  PGSSLMODE=disable
```

More info
For more information about data storage, read [full PostgreSQL page](https://docs.sourcegraph.com/dev/background-information/postgresql).

Migrations are applied automatically.

## Configure HTTPS reverse proxy
- Sourcegraph’s development environment ships with a Caddy 2 HTTPS reverse proxy that allows you to access your local sourcegraph instance via https://sourcegraph.test:3443 (a fake domain with a self-signed certificate that’s added to /etc/hosts).
- If you’d like Sourcegraph to be accessible under https://sourcegraph.test (port 443) instead, you can set up authbind and set the environment variable SOURCEGRAPH_HTTPS_PORT=443.

### Prerequisites
In order to configure the HTTPS reverse-proxy, you’ll need to edit /etc/hosts and initialize Caddy 2.

Add sourcegraph.test to /etc/hosts
sourcegraph.test needs to be added to /etc/hosts as an alias to 127.0.0.1. There are two main ways of accomplishing this:

Manually append 127.0.0.1 sourcegraph.test to /etc/hosts
Use the provided ./dev/add_https_domain_to_hosts.sh convenience script (sudo may be required).

```
> ./dev/add_https_domain_to_hosts.sh
```

```
# /etc/hosts
...
127.0.0.1        localhost sourcegraph.test
...
```

### Initialize Caddy 2

Caddy 2 automatically manages self-signed certificates and configures your system so that your web browser can properly recognize them. The first time that Caddy runs, it needs root/sudo permissions to add its keys to your system’s certificate store. You can get this out the way after installing Caddy 2 by running the following command and entering your password if prompted:

```
./dev/caddy.sh trust
```

Note: If you are using Firefox and have a master password set, the following prompt will come up first:

```
Enter Password or Pin for "NSS Certificate DB":
```

Enter your Firefox master password here and proceed. See this issue on GitHub for more information.

You might need to restart your web browsers in order for them to recognize the certificates.

## Start the server (TODO: no sg at all!)

Configure sg to connect to databases
If you chose to run PostgreSQL and Redis without Docker they should already be running. You can jump the next section.

- If you are a Sourcegraph employee: start the local development server for Sourcegraph Enterprise with the following command: `sg start`
- If you are not a Sourcegraph employee and don’t have access to the dev-private repository: you want to start Sourcegraph OSS, do this: `sg start oss`

Navigate your browser to https://sourcegraph.test:3443 to see if everything worked.

If sg exits with errors or outputs errors, take a look at Troubleshooting or ask in the #dev-experience Slack channel.
