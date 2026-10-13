from routes.PatientRegRoutes import router as patient_registration_router
from routes.PatientProfileRoutes import router as patient_profile_router
from routes.Authentication import authRouter

__all__ = ["patient_registration_router", "patient_profile_router", "authRouter"]

