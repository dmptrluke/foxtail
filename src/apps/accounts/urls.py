from django.urls import path

from apps.accounts import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='account_profile'),
    path('profile/', views.UserView.as_view(), name='account_profile_edit'),
    path('signup/', views.CSPSignupView.as_view(), name='account_signup'),
    path('password/reset/', views.CSPPasswordResetView.as_view(), name='account_reset_password'),
    path('applications/', views.ConsentList.as_view(), name='account_application_list'),
    path('applications/<str:pk>/revoke/', views.ConsentRevoke.as_view(), name='account_application_revoke'),
    path('verification/', views.VerificationView.as_view(), name='account_verification'),
    path('verification/generate/', views.GenerateTokenView.as_view(), name='account_verification_generate'),
    path('verification/confirm/', views.ConfirmVerificationView.as_view(), name='account_verification_confirm'),
    path('verification/verify/', views.VerifyUserView.as_view(), name='account_verification_verify'),
    path('verification/unverify/', views.UnverifyUserView.as_view(), name='account_verification_unverify'),
    path('2fa/authenticate/', views.MFAAuthenticateView.as_view(), name='mfa_authenticate'),
]
