### 1. Setup & Configuration
- [x] Set up Python project with FastAPI and required dependencies (elasticsearch-py, pydantic, etc.)
- [x] Configure Elasticsearch connection with given credentials
- [x] Create configuration management (environment variables for credentials)

### 2. Elasticsearch Integration
- [x] Implement connection to test Elasticsearch server
- [x] Create search function with query capabilities
- [x] Implement media URL construction logic (padding zeros, DB value handling)
- [x] Handle potential connection errors and timeouts

### 3. API Endpoints
- [x] Design RESTful endpoint (GET) `/api/media/search`
- [x] Add pagination support for search results
- [x] Implement health check endpoint (`/health`)

### 4. Data Processing
- [x] Implement data normalization for inconsistent fields
- [x] Create response models to standardize output format
- [x] Handle missing/empty fields gracefully
- [x] Add field mapping for better searchability
- [x] Implement request validation with Pydantic models

### 5. Error Handling
- [x] Implement custom exception handling
- [x] Create proper HTTP error responses
- [x] Handle Elasticsearch-specific errors
- [x] Implement retry logic

### 6. Testing
- [x] Write unit tests for core functions
- [x] Injection attacks / input sanitization
- [x] Write end-to-end tests for API endpoints
- [x] Write performance tests for API endpoints

### 7. Logging & Caching
- [x] Logging: Set up basic request logging
- [x] Caching: Implement caching

### 8. Deployment
- [x] Create Dockerfile
- [x] Create Docker Compose
- [x] Create K8s
- [x] Add basic GitHub Action CI/CD

### 9. Documentation
- [x] Write API documentation (OpenAPI/Swagger via FastAPI)
- [x] Create README

### 10. Problem Identification & Solution
- [x] Identify at least one key issue
- [x] Document the problem and its impact
- [x] Propose solution with justification

### 11. Scalability & Maintainability
- [x] Handle large volume of data
- [x] New provider and media

### 12. Final Review
- [x] Check TODOs
- [x] Code quality check
- [x] Verify all requirements are addressed
- [ ] Remove all passwords before final deployment
- [ ] Prepare submission package
