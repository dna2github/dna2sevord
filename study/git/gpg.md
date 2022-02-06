# gpg sign for git commit

```
# gpg --full-gen-key
# gpg --list-secret-keys --keyid-format LONG <your_email>
# gpg --armor --export <sec/hash>
> copy <output> to gitlab/github and add GPG key
# git config user.signingkey <sec/hash>
# git commit -S
(gpg2) # export GPG_TTY=$(tty)
(no-need -S) # git config commit.gpgsign true
```
