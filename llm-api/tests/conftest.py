"""Pytest configuration and fixtures."""
import pytest
import os
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv(".env.example")

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["DEBUG"] = "true"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["API_KEY_SECRET"] = "test-api-key"
