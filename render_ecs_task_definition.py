import argparse
import json


def replace_ecs_task_definition():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--aws_is_prod", type=str)
    parser.add_argument("--aws_account_id", type=str)
    parser.add_argument("--aws_region", type=str)
    parser.add_argument("--aws_region_name", type=str)
    parser.add_argument("--ecr_repository_name", type=str)
    parser.add_argument("--aws_secret_name", type=str)
    parser.add_argument("--aws_access_key_id", type=str)
    parser.add_argument("--aws_secret_access_key", type=str)
    parser.add_argument("--aws_secret_name_prod", type=str)
    args = parser.parse_args()

    is_prod = args.aws_is_prod

    if is_prod == "true":
        file_name = "ecs-task-prod-def.json"
    else:
        file_name = "ecs-task-def.json"

    with open(file_name, 'r') as file:
        task_definition = json.load(file)

    global key_map
    key_map = {
        "AWS_ACCOUNT_ID": args.aws_account_id,
        "AWS_REGION": args.aws_region,
        "AWS_REGION_NAME": args.aws_region_name,
        "ECR_REPOSITORY_NAME": args.ecr_repository_name,
        "ECR_REPOSITORY_NAME_PROD": args.ecr_repository_name,
        "AWS_SECRET_NAME": args.aws_secret_name,
        "AWS_ACCESS_KEY_ID": args.aws_access_key_id,
        "AWS_SECRET_ACCESS_KEY": args.aws_secret_access_key,
        "AWS_SECRET_NAME_PROD": args.aws_secret_name_prod,
    }
    

    def render_ecs_task_definition(obj):
        if isinstance(obj, dict):
            return {k: render_ecs_task_definition(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [render_ecs_task_definition(v) for v in obj]
        elif isinstance(obj, str) and "$" in obj:
            replace_map = dict()
            env_var = obj.replace(" ", "").split("${{")
            env_real_var = []
            for ev in env_var:
                env_real_var.append(ev.split("}}")[0])
        
            for erv in env_real_var:
                if not erv.startswith("secrets"):
                    continue
                secret_value = erv.replace("}}", "").split(".")
                category, name = secret_value[0], secret_value[1]
                if category != 'secrets':
                    continue
                replaced_name = key_map.get(name)
                replace_map[name] = replaced_name

            for k, v in replace_map.items():
                replaced_string = "${{ secrets." + k + " }}"
                obj = obj.replace(replaced_string, v)
            
            return obj
        return obj

    task_definition = render_ecs_task_definition(task_definition)
    with open(file_name, 'w') as file:
        json.dump(task_definition, file, indent=2)


if __name__ == "__main__":
    result = replace_ecs_task_definition()
