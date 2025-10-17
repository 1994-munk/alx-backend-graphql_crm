from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt  # Disable CSRF for GraphQL testing
from alx_backend_graphql.schema import schema



urlpatterns = [
    path('admin/', admin.site.urls),

    # 👇 Add GraphQL endpoint
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
]

