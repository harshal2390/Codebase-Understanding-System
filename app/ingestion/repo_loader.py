import os
from git import Repo


class RepoLoader:
    def __init__(self, repo_url: str, save_path: str = "data/repos"):
        self.repo_url = repo_url
        self.save_path = save_path

        # Extract repo name from URL
        self.repo_name = repo_url.split("/")[-1].replace(".git", "")
        self.repo_path = os.path.join(save_path, self.repo_name)

    def clone_repo(self):
        """
        Clone repo if not already present
        """
        if os.path.exists(self.repo_path):
            print(f"[INFO] Repo already exists at {self.repo_path}")
            return self.repo_path

        print(f"[INFO] Cloning repo from {self.repo_url}...")

        Repo.clone_from(self.repo_url, self.repo_path)

        print(f"[SUCCESS] Repo cloned at {self.repo_path}")
        return self.repo_path