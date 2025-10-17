# schema.py
import graphene  # Graphene is the library that handles GraphQL in Django

# 🧠 Define a simple Query class
class Query(graphene.ObjectType):
    # Create a field named 'hello' that returns a String
    hello = graphene.String()

    # Define what happens when someone queries the 'hello' field
    def resolve_hello(root, info):
        # This function is called whenever someone requests { hello }
        return "Hello, GraphQL!"

# 🔗 Combine all queries into a schema
schema = graphene.Schema(query=Query)
