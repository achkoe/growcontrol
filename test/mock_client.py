import argparse
import xmlrpc.client
import test.tst_configuration as tst_configuration


proxy = xmlrpc.client.ServerProxy(f"http://localhost:{tst_configuration.mock_server_port}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--moisture", action="store_true")
    parser.add_argument("--value", type=int)
    args = parser.parse_args()
    if args.moisture is not None and args.value is not None:
        print(f"moisture -> {args.value}")
        proxy.set_value(args.value)
    
    