#!/usr/bin/env python3
import os


def debug_environment():
    print("=" * 50)
    print("🔍 RAILWAY DEBUG")
    print("=" * 50)

    # Variables importantes
    vars_to_check = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "REDIS_URL": os.getenv("REDIS_URL"),
        "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT"),
        "PORT": os.getenv("PORT")
    }

    for var_name, var_value in vars_to_check.items():
        if var_value:
            if "API_KEY" in var_name:
                display = f"{var_value[:8]}..." if len(var_value) > 8 else "***"
            else:
                display = var_value
            print(f"✅ {var_name}: {display}")
        else:
            print(f"❌ {var_name}: NOT SET")

    print("=" * 50)


if __name__ == "__main__":
    debug_environment()