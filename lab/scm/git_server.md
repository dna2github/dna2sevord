doc:
- https://git-scm.com/docs
- https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain
- https://git-scm.com/book/en/v2/Git-Internals-Transfer-Protocols

hash conlision:
- https://stackoverflow.com/questions/10434326/hash-collision-in-git
- https://github.blog/2017-03-20-sha-1-collision-detection-on-github-com/
- https://github.com/cr-marcstevens/sha1collisiondetection

how to show file list:
- https://stackoverflow.com/questions/424071/how-to-list-all-the-files-in-a-commit

```
git diff-tree --no-commit-id --name-only -r <commit-ish>
git ls-tree --name-only -r <commit-ish>
git ls-tree --name-only <commit-ish> -- <path>

git show --stat --oneline HEAD
git show --stat --oneline b24f5fb
git show --stat --oneline HEAD^^..HEAD

git show --name-only --oneline HEAD
git show --name-only --oneline b24f5fb
git show --name-only --oneline HEAD^^..HEAD

git show --pretty="format:" --name-only START_COMMIT..END_COMMIT | sort | uniq
git diff --name-only START_COMMIT..END_COMMIT
git diff --name-status START_COMMIT..END_COMMIT
git log -1 --oneline --name-status <commit-hash>
```

how to show file content:
- https://stackoverflow.com/questions/338436/how-can-i-view-an-old-version-of-a-file-with-git

```
git show <commitHash>:/path/to/file
```

how to get blame for lines:

```
git blame -e -l [-L <start>,<end>] <revision> -- <path>
```

how to get commits for file:

```
git log --pretty=format:%H -- <path>
```
