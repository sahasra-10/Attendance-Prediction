import hashlib
import pandas as pd

# ================================
# Password Hashing
# ================================
def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


# ================================
# Login Validation
# ================================
def check_login(username: str, password: str, users_df: pd.DataFrame):
    """Check if username and hashed password match."""
    hashed = hash_password(password)
    user = users_df[
        (users_df['username'].astype(str) == str(username))
        & (users_df['password'] == hashed)
    ]
    if not user.empty:
        return user.iloc[0]['role']
    return None


# ================================
# Attendance Reader (Smart Header Finder)
# ================================
def read_attendance(path_or_buffer, max_header_rows: int = 6) -> pd.DataFrame:
    """
    Read an attendance CSV even if the header starts after a few rows.
    Will try headers from row 0 to max_header_rows - 1.

    Args:
        path_or_buffer: Path or buffer to the CSV file.
        max_header_rows: How many top rows to check for headers.

    Returns:
        Cleaned DataFrame with stripped column names.
    """
    last_exc = None
    for header in range(max_header_rows):
        try:
            if hasattr(path_or_buffer, 'seek'):
                try:
                    path_or_buffer.seek(0)
                except Exception:
                    pass

            df = pd.read_csv(path_or_buffer, header=header)
            df.columns = df.columns.astype(str).str.strip()

            # Ensure Roll.No column exists before returning
            if 'Roll.No' in df.columns:
                return df

        except Exception as e:
            last_exc = e
            continue

    # Fallback if not found in first few rows
    if hasattr(path_or_buffer, 'seek'):
        try:
            path_or_buffer.seek(0)
        except Exception:
            pass

    df = pd.read_csv(path_or_buffer)
    df.columns = df.columns.astype(str).str.strip()
    return df
