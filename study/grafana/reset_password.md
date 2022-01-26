# reset password

> ref: https://community.grafana.com/t/admin-password-reset/19455

```
$ sudo sqlite3 /var/lib/grafana/grafana.db

# set password as admin; next when user login, it will require change password then.
sqlite> update user set password = '59acf18b94d7eb0694c61e60ce44c110c7a683ac6a8f09580d626f90f4a242000746579358d77dd9e570e83fa24faa88a8a6', salt = 'F3FAxVm33R' where login = 'admin';
sqlite> .exit
```
