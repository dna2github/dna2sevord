# Dgraph basic op

- go build -tags 'oss' -o dgraph /path/to/source/dgraph/main.go
- dgraph zero --telemetry "sentry=false;reports=false;"
- dgraph alpha --telemetry "sentry=false;reports=false;" --lambda "num=0;"
- curl -X POST -H "Content-Type: application/graphql" http://127.0.0.1:8080/admin/schema -d @schema.graphql
- curl -X POST -H "Content-Type: application/graphql" http://127.0.0.1:8080/graphql -d @todo.graphql
- curl -X POST -H "Content-Type: application/graphql" http://127.0.0.1:8080/graphql -d @query2.graphql | python3 -m json.tool

```graphql
"""
schema.graphql
"""

type Task {
    id: ID!
    title: String! @search(by: [fulltext, trigram])
    completed: Boolean! @search
    user: User!
}

type User {
    username: String! @id
    name: String
    tasks: [Task] @hasInverse(field: user)
}
```

```graphql
# todo.graphql

mutation {
  addUser(input: [
    {
      username: "alice@dgraph.io",
      name: "Alice",
      tasks: [
        {
          title: "Avoid touching your face",
          completed: false,
        },
        {
          title: "Stay safe",
          completed: false
        },
        {
          title: "Avoid crowd",
          completed: true,
        },
        {
          title: "Wash your hands often",
          completed: true
        }
      ]
    }
  ]) {
    user {
      username
      name
      tasks {
        id
        title
      }
    }
  }
}
```

```graphql
# query.graphql

query {
  queryTask {
    id
    title
    completed
    user {
        username
    }
  }
}

# query2.graphql
query {
  queryTask(filter: {
    completed: true
  }) {
    title
    completed
  }
}

# query3.graphql
query {
  queryTask(filter: {
    title: {
      alloftext: "avoid"
    }
  }) {
    id
    title
    completed
  }
}
```
