
# System Use Case Diagram

## Overview
This document illustrates the primary use cases for the **Being Geul Youth Policy Platform**, showing how different actors interact with the system's features.

## Actors
1. **Guest**: A visitor who has not logged in.
2. **User**: A focused, logged-in member seeking youth policies.
3. **Admin**: A system administrator managing the platform content.

## Use Case Diagram (Mermaid)

```mermaid
usecaseDiagram
    %% Actor Definitions
    actor "Guest" as G
    actor "User" as U
    actor "Admin" as A

    %% System Boundary
    package "Being Geul Platform" {
        
        %% Guest Use Cases
        usecase "View Landing Page" as UC_ViewLanding
        usecase "Sign Up" as UC_SignUp
        usecase "Login" as UC_Login
        
        %% Main Discovery
        usecase "View Main Recommendations" as UC_ViewMain
        usecase "Swipe Policies (Like/Pass)" as UC_Swipe
        usecase "View Policy Details (Modal)" as UC_ViewDetail
        
        %% Search & Filter
        usecase "Search Policies" as UC_Search
        usecase "Filter by Region/Genre" as UC_Filter
        
        %% My Page / Personalization
        usecase "View My Page" as UC_MyPage
        usecase "Manage Liked Policies" as UC_ManageLikes
        usecase "View Policy MBTI" as UC_ViewMBTI
        usecase "Edit Profile / Avatar" as UC_EditProfile
        
        %% Admin
        usecase "Manage Policy Data" as UC_ManagePolicy
        usecase "View User Stats" as UC_ViewStats
    }

    %% Relationships - Guest
    G --> UC_ViewLanding
    G --> UC_SignUp
    G --> UC_Login

    %% Relationships - User
    U --> UC_ViewMain
    U --> UC_Swipe
    U --> UC_ViewDetail
    U --> UC_Search
    U --> UC_Filter
    U --> UC_MyPage
    U --> UC_ManageLikes
    U --> UC_ViewMBTI
    U --> UC_EditProfile

    %% Inheritance: User can do everything a Guest can (conceptually)
    G <|-- U

    %% Relationships - Admin
    A --> UC_Login
    A --> UC_ManagePolicy
    A --> UC_ViewStats
    
    %% Include/Extend relationships
    UC_Search ..> UC_Filter : <<include>>
    UC_ViewMain ..> UC_ViewDetail : <<extend>>
    UC_Swipe ..> UC_ViewDetail : <<extend>>
```

## Key Workflows

### 1. Policy Discovery (Main Loop)
- **Actor**: User
- **Flow**: User logs in -> Views Main Page -> Swipes Cards (Like/Pass) -> Clicks for Detail -> System updates preferences.

### 2. Personalized Dashboard (My Page)
- **Actor**: User
- **Flow**: User accesses My Page -> Checks MBTI Type -> Reviews "Liked" Policies -> Updates Profile Avatar.
