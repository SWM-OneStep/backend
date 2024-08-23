import argparse
import json


def replace_ecs_task_definition():

    with open('ecs-task.json', 'r') as file:
        task_definition = json.load(file)

    parser = argparse.ArgumentParser()
    parser.add_argument("--aws_account_id", type=str)
    parser.add_argument("--aws_region", type=str)
    parser.add_argument("--aws_region_name", type=str)
    parser.add_argument("--ecr_repository_name", type=str)
    parser.add_argument("--aws_secret_name", type=str)
    parser.add_argument("--aws_access_key_id", type=str)
    parser.add_argument("--aws_secret_access_key", type=str)
    parser.add_argument("--aws_secret_name_prod", type=str)
    args = parser.parse_args()

    global key_map
    key_map = {
        "AWS_ACCOUNT_ID": args.aws_account_id,
        "AWS_REGION_NAME": args.aws_region,
        "AWS_REGION_NAME": args.aws_region_name,
        "ECR_REPOSITORY_NAME": args.ecr_repository_name,
        "AWS_SECRET_NAME": args.aws_secret_name,
        "AWS_ACCESS_KEY_ID": args.aws_access_key_id,
        "AWS_SECRET_ACCESS_KEY": args.aws_secret_access_key,
        "AWS_SECRET_NAME_PROD": args.aws_secret_name_prod,
    }
    

    def render_ecs_task_definition(obj):
        print(obj)
        if isinstance(obj, dict):
            return {k: render_ecs_task_definition(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [render_ecs_task_definition(v) for v in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            env_var = obj.strip()[9:-1] # remove ${secrets.} from string
            return key_map.get(env_var)
        return obj

    task_definition = render_ecs_task_definition(task_definition)
    with open('ecs-task.json', 'w') as file:
            json.dump(task_definition, file, indent=2)


if __name__ == "__main__":
    result = replace_ecs_task_definition()
    print("----result-----\n", result)
