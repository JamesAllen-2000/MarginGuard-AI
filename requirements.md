# Requirements Document: MarginGuard AI - Hackathon MVP

## Introduction

MarginGuard AI is a real-time profit risk intelligence platform for Amazon FBA sellers. This hackathon MVP focuses on delivering a working demonstration of core profit risk detection capabilities using synthetic data and simplified architecture. The system enables sellers to identify at-risk SKUs before profit erosion occurs, understand why through AI-generated explanations, and simulate corrective actions.

## Glossary

- **SKU**: Stock Keeping Unit - a unique identifier for each product variant
- **Margin_Risk_Score**: A numerical value (0-100) indicating the likelihood of profit erosion for a SKU
- **Risk_Engine**: The component that calculates margin risk scores based on multiple factors
- **Explanation_Generator**: The AI component that produces natural language explanations using Amazon Bedrock
- **Profit_Health_Radar**: A visual dashboard component displaying SKU health status
- **What_If_Simulator**: The component that models the impact of price or cost changes
- **Synthetic_Data_Store**: Pre-loaded sample Amazon seller data stored in S3
- **FBA**: Fulfillment by Amazon - Amazon's warehousing and shipping service
- **API_Gateway**: AWS service that handles HTTP requests to backend Lambda functions
- **Lambda_Function**: Serverless compute function that processes business logic
- **Bedrock**: Amazon's managed AI service for generating natural language content
- **Amplify**: AWS hosting service for the React frontend
- **Cognito**: AWS authentication and user management service

## Requirements

### Requirement 1: User Authentication

**User Story:** As an Amazon seller, I want to securely log into the platform, so that I can access my profit risk intelligence dashboard.

#### Acceptance Criteria

1. WHEN a user navigates to the application, THE System SHALL display a login interface
2. WHEN a user provides valid credentials, THE Cognito SHALL authenticate the user and grant access
3. WHEN a user provides invalid credentials, THE System SHALL display an error message and prevent access
4. WHEN an authenticated user closes the browser, THE System SHALL maintain the session for 24 hours
5. THE System SHALL support user registration with email and password

### Requirement 2: Synthetic Data Loading

**User Story:** As a demo user, I want the system to load pre-built sample data, so that I can immediately see profit risk analysis without connecting real Amazon accounts.

#### Acceptance Criteria

1. WHEN the system initializes, THE Synthetic_Data_Store SHALL contain 20-50 sample SKUs with complete historical data
2. THE Synthetic_Data_Store SHALL include margin trends, ad spend, fees, returns, and pricing data for each SKU
3. WHEN a user logs in, THE System SHALL load the synthetic dataset within 2 seconds
4. THE Synthetic_Data_Store SHALL represent realistic Amazon FBA seller scenarios including profitable, at-risk, and loss-making SKUs
5. THE System SHALL store synthetic data in S3 in JSON format

### Requirement 3: Margin Risk Score Calculation

**User Story:** As an Amazon seller, I want to see a risk score for each SKU, so that I can quickly identify which products need attention.

#### Acceptance Criteria

1. WHEN the Risk_Engine processes a SKU, THE System SHALL calculate a Margin_Risk_Score between 0 and 100
2. THE Risk_Engine SHALL incorporate margin trend analysis (declining margins increase risk)
3. THE Risk_Engine SHALL incorporate ad spend efficiency (high ACOS increases risk)
4. THE Risk_Engine SHALL incorporate fee changes (increasing fees increase risk)
5. THE Risk_Engine SHALL incorporate return rates (high returns increase risk)
6. WHEN a SKU has declining margins over 30 days, THE Risk_Engine SHALL assign a score above 60
7. WHEN a SKU has stable or improving margins, THE Risk_Engine SHALL assign a score below 40
8. THE System SHALL recalculate risk scores when underlying data changes

### Requirement 4: AI-Powered Risk Explanations

**User Story:** As an Amazon seller, I want to understand why a SKU is at risk, so that I can take informed corrective action.

#### Acceptance Criteria

1. WHEN a user selects a SKU, THE Explanation_Generator SHALL produce a natural language explanation within 3 seconds
2. THE Explanation_Generator SHALL use Amazon Bedrock to generate explanations
3. THE Explanation_Generator SHALL include the top 3 risk factors contributing to the score
4. THE Explanation_Generator SHALL provide specific data points (e.g., "Ad spend increased 45% while sales grew only 12%")
5. WHEN a SKU has multiple risk factors, THE Explanation_Generator SHALL prioritize factors by impact magnitude
6. THE Explanation_Generator SHALL generate explanations in clear, non-technical language suitable for business users
7. THE System SHALL cache explanations to avoid redundant API calls to Bedrock

### Requirement 5: Profit Health Radar Visualization

**User Story:** As an Amazon seller, I want to see all my SKUs visualized on a health radar, so that I can understand my portfolio health at a glance.

#### Acceptance Criteria

1. WHEN a user views the dashboard, THE Profit_Health_Radar SHALL display all SKUs as visual elements
2. THE Profit_Health_Radar SHALL use color coding to indicate risk levels (green: 0-39, yellow: 40-69, red: 70-100)
3. THE Profit_Health_Radar SHALL position SKUs based on two dimensions: profit margin and sales velocity
4. WHEN a user hovers over a SKU, THE System SHALL display a tooltip with SKU name, risk score, and current margin
5. WHEN a user clicks a SKU on the radar, THE System SHALL navigate to the detailed view with AI explanation
6. THE Profit_Health_Radar SHALL update within 1 second when filters are applied
7. THE Profit_Health_Radar SHALL be responsive and render correctly on desktop screens (1920x1080 minimum)

### Requirement 6: What-If Price Simulation

**User Story:** As an Amazon seller, I want to simulate price changes, so that I can understand the impact on profitability before making changes in Amazon Seller Central.

#### Acceptance Criteria

1. WHEN a user selects a SKU, THE System SHALL display a what-if simulation interface
2. WHEN a user adjusts the price slider, THE What_If_Simulator SHALL recalculate projected margin within 500ms
3. THE What_If_Simulator SHALL calculate the impact on profit margin based on price elasticity assumptions
4. THE What_If_Simulator SHALL display the new projected Margin_Risk_Score after the price change
5. WHEN a price increase is simulated, THE What_If_Simulator SHALL estimate the impact on sales velocity
6. WHEN a price decrease is simulated, THE What_If_Simulator SHALL estimate the impact on sales volume
7. THE What_If_Simulator SHALL allow price adjustments between -50% and +100% of current price
8. THE System SHALL display before/after comparison metrics (margin, risk score, projected revenue)

### Requirement 7: SKU List and Filtering

**User Story:** As an Amazon seller, I want to view and filter my SKU list, so that I can focus on specific products or risk categories.

#### Acceptance Criteria

1. WHEN a user views the dashboard, THE System SHALL display a sortable table of all SKUs
2. THE System SHALL display SKU name, current margin, risk score, and trend indicator for each row
3. WHEN a user clicks a column header, THE System SHALL sort the table by that column
4. THE System SHALL support filtering by risk level (Low: 0-39, Medium: 40-69, High: 70-100)
5. WHEN a user applies a filter, THE System SHALL update both the table and Profit_Health_Radar within 1 second
6. THE System SHALL support search by SKU name or identifier
7. THE System SHALL display the count of SKUs in each risk category

### Requirement 8: Backend API Architecture

**User Story:** As a system architect, I want a serverless API architecture, so that the demo scales efficiently and minimizes infrastructure management.

#### Acceptance Criteria

1. THE API_Gateway SHALL expose RESTful endpoints for all frontend operations
2. THE System SHALL implement Lambda_Functions for risk calculation, explanation generation, and simulation
3. WHEN an API request is received, THE API_Gateway SHALL route it to the appropriate Lambda_Function
4. THE Lambda_Functions SHALL retrieve synthetic data from the Synthetic_Data_Store in S3
5. THE System SHALL return API responses within 3 seconds for 95% of requests
6. THE API_Gateway SHALL implement CORS headers to allow requests from the Amplify-hosted frontend
7. THE System SHALL use AWS IAM roles for secure access between services

### Requirement 9: Frontend Deployment

**User Story:** As a developer, I want the React frontend deployed on AWS Amplify, so that the demo is accessible via a public URL.

#### Acceptance Criteria

1. THE System SHALL host the React application on AWS Amplify
2. WHEN the application is deployed, THE Amplify SHALL provide a public HTTPS URL
3. THE System SHALL build and deploy the frontend within 5 minutes of code changes
4. THE Frontend SHALL integrate with Cognito for authentication
5. THE Frontend SHALL make API calls to the API_Gateway endpoints
6. THE System SHALL serve static assets (CSS, JavaScript, images) with CDN caching

### Requirement 10: Demo Flow Optimization

**User Story:** As a hackathon presenter, I want a streamlined demo flow, so that I can showcase the platform's value in under 5 minutes.

#### Acceptance Criteria

1. WHEN a demo user logs in, THE System SHALL display the Profit_Health_Radar as the landing page
2. THE System SHALL pre-select a high-risk SKU to demonstrate the AI explanation feature
3. THE System SHALL provide a "Demo Mode" that highlights key features in sequence
4. WHEN Demo Mode is activated, THE System SHALL display tooltips guiding the user through the workflow
5. THE System SHALL complete the full demo flow (login → radar view → SKU detail → AI explanation → what-if simulation) within 5 minutes
6. THE System SHALL include sample data that tells a compelling story (e.g., a SKU saved by price adjustment)
