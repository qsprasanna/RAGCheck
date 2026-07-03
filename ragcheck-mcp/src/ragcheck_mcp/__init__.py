def main():
    import asyncio
    from .server import main as server_main
    asyncio.run(server_main())
