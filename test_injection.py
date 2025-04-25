from roblox_injector import RobloxInjector

def main():
    injector = RobloxInjector()
    success, msg = injector.inject()
    print(f"Injection result: {success}, {msg}")

    if success:
        test_script = """
        print("Hello from Roblox!")
        workspace = game:GetService("Workspace")
        print("Workspace found:", workspace)
        """
        success, msg = injector.execute_script(test_script)
        print(f"Script execution result: {success}, {msg}")

if __name__ == "__main__":
    main()
