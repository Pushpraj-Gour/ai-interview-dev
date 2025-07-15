from fastapi import HTTPException, Depends
from fastapi import Depends
from fastapi import HTTPException, status
import secrets
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
# from firebase_admin import auth
from app.config import keys

http_basic_security = HTTPBasic()

def _basic_auth(credentials: HTTPBasicCredentials, correct_username, correct_password):
	current_username_bytes = credentials.username.encode("utf8")
	correct_username_bytes = correct_username.encode("utf8")
	is_correct_username = secrets.compare_digest(
		current_username_bytes, correct_username_bytes
	)
	
	current_password_bytes = credentials.password.encode("utf8")
	correct_password_bytes = correct_password.encode("utf8")
	is_correct_password = secrets.compare_digest(
		current_password_bytes, correct_password_bytes
	)

	if not (is_correct_username and is_correct_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Unauthorized",
			headers={"WWW-Authenticate": "Basic"},
		)

def basic_auth(credentials: HTTPBasicCredentials = Depends(http_basic_security)):
	return _basic_auth(credentials, keys.basic_auth_username, keys.basic_auth_password)