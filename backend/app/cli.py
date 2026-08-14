import argparse
from sqlalchemy import select
from app.db import SessionLocal
from app.models.simulation import User

def main():
    parser = argparse.ArgumentParser(description="AI Simulation Focus Group administration")
    sub = parser.add_subparsers(dest="command", required=True)
    promote = sub.add_parser("promote-admin"); promote.add_argument("email")
    args = parser.parse_args()
    if args.command == "promote-admin":
        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.email == args.email.lower()))
            if not user: raise SystemExit(f"User not found: {args.email}")
            user.role = "ADMIN"; db.commit(); print(f"Promoted {user.email} to ADMIN")

if __name__ == "__main__": main()
