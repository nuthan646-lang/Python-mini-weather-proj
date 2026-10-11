import requests,time
def main():
   while True:
      start=time.time()
      choice=display()
      if choice=='1' or choice=="search for a repo":
         search_repo()
         pass
      elif choice=='2' or choice=="get repo details":
         get_repo_details()
         pass
      elif choice=='3' or choice=="exit":
         print("Exiting the program...")
         end=time.time()
         print(f"Total time taken: {end-start:.2f} seconds")
         break

      else:
         print("Invalid choice. Please try again.")

def display():
      print("==========================================\n\n"
            "             GITHUB REPO TOOL             \n\n"
            "==========================================\n\n"
            "1. Search for a repo\n"
            "2. get repo details\n"
            "3. Exit\n")
      choice = input("Enter your choice: ").strip().lower()

      return choice

def search_repo():
      query = input("Enter the repository name to search: ").strip()
      url = f"https://api.github.com/search/repositories?q={query}"
      response = requests.get(url)

      if response.status_code==200:
         data=response.json()
         items=data.get("items", [])
         if len(items)>0:
             print(f"found {len(items)} repositories\n")
         else:
               print("No repositories found.\n")
         




main()
