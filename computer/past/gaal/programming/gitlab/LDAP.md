# LDAP without providing its super user

> In Gitlab LDAP configuration requires providing username and password of a super user. However, there may not exist in Active Directory server.

Thus it needs some manual work. The file path is based on official dockerized Gitlab. How to: `docker run gitlab` `docker exec -it gitlab-container-name /bin/bash`

### Definitely enable LDAP feature in Gitlab configuration:

> /etc/gitlab/gitlab.rb

```ruby
gitlab_rails['ldap_enabled'] = true
gitlab_rails['ldap_servers'] = YAML.load <<-'EOS!!!' # remember to close this block with 'EOS' below
  main: # 'main' is the GitLab 'provider ID' of this LDAP server
    label: 'Internal LDAP'
    host: 'ldap.example.com'
    port: 389
    uid: ''
    password: ''
    bind_dn: ''
    method: 'plain' # "tls" or "ssl" or "plain"
    active_directory: true
    allow_username_or_email_login: true
    block_auto_created_users: false
    base: ''
    user_filter: ''
    attributes:
      username: ['uid', 'userid', 'sAMAccountName']
      email:    ['email', 'mail', 'userPrincipalName']
EOS!!!
```

### Transport username instead of filter:

> GITLAB_GEM_HOME=/opt/gitlab/embedded/service/gem/ruby/2.1.0, $GITLAB_GEM_HOME/gems/gitlab_omniauth-ldap-1.2.1/lib/omniauth/strategies/ldap.rb

```ruby
# in OmniAuth::Strategies::LDAP.callback_phase
# ...
  # pass username instead of filter to adapter
  #@ldap_user_info = @adaptor.bind_as(:filter => filter(@adaptor), :size => 1, :password => request['password'])
  @ldap_user_info = @adaptor.bind_as(:size => 1, :password => request['password'], :username => request['username'])
# ...
```

### Make input username and password as connection parameters:

> $GITLAB_GEM_HOME/gitlab_omniauth-ldap-1.2.1/lib/omniauth-ldap/adaptor.rb

```ruby
# in OmniAuth::LDAP::Adaptor.bind_as
  # comment out whole bind_as definition
  def bind_as(args={})
    result = {}
    result[:uid] = ["#{args[:username]}"]
    result[:email] = ["#{args[:username]}@example.com"]
    login = "#{args[:username]}@example.com"
    password = args[:password]
    config = {
      :host => @host,
      :port => @port,
      :encryption => method,
      :base => @base
      :auth => {}
    }
    config[:auth][:method] = @bind_method
    config[:auth][:username] = login
    config[:auth][:password] = password
    @connection = Net::LDAP.new(config)
    false
    result if @connection.bind
  end
```

### Simply avoid blocking user:

> GITLAB_RAILS_HOME=/opt/gitlab/embedded/service/gitlab-rails $GITLAB_RAILS_HOME/app/controllers/application_controller.rb

ApplicationController.ldap_security_check: add one line at the first `return true`

> $GITLAB_RAILS_HOME/app/controllers/omniauth_callbacks_controller.rb

OmniauthCallbacksController.ldap: `if ldap_user.allowed?` => `if true`

> $GITLAB_RAILS_HOME/lib/gitlab/ldap/access.rb

Gitlab::LDAP::Access.(self.allowed?): add `return true` as first line

### Simply connect to user model:

> $GITLAB_RAILS_HOME/lib/gitlab/ldap/user.rb

Gitlab::LDAP::User.gl_user: `@gl_user ||= find_by_uid_and_provider || find_by_email || build_new_user` => `@gl_user ||= find_by_email || build_new_user`

> $GITLAB_RAILS_HOME/lib/gitlab/o_auth/user.rb

Gitlab::OAuth::User.user_attributes: `username = ldap_person.username.presence` => `username = ldap_person.email.first.presence.split('@').first`

### Make sure `git push` works:

> $GITLAB_RAILS_HOME/lib/gitlab/ldap/authentication.rb

```
In "Linux", after "git clone" a repo with protocoal of http/https,
it requires "git remote set-url origin http/https://<username>@xxxx/xx/x.git".
Then "git push" will prompt a line for password.

In "MacOSX", "git push" will ask username and password.
```

```ruby
# workflow: app/controllers/projects/git_http_controller.rb => lib/gitlab/auth.rb => lib/gitlab/ldap/authentication.rb
# Gitlab::LDAP::Authentication
#   .login:
# ...
  #filter: user_filter(login),
  username: login,
# ...

#   .user:
# ...
#  #Gitlab::LDAP::User.find_by_uid_and_provider(ldap_user.dn, provider)
#  Gitlab::LDAP::User.find_by_email(ldap_user[:email].first)
# ...
```
