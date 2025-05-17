# NOTE: The "compatible-with" in the header is a versioning system used by Elasticsearch to ensure that the client and server can communicate effectively.
# It allows for backward compatibility with older versions of Elasticsearch while still taking advantage of new features in newer versions.
# The "8" in "compatible-with=8" indicates that the client is compatible with version 8 of Elasticsearch.
# This should only be changed if the server version changes and the client needs to be compatible with a different version.

ES_MIME_TYPE = "application/vnd.elasticsearch+json; compatible-with=8"
HEADER = {
    "Accept": ES_MIME_TYPE,
    "Content-Type": ES_MIME_TYPE,
}

INDEX = "imago"
