import docker
from kubernetes import client, config

class DeploymentManager:
    def __init__(self, environment='prod'):
        self.environment = environment
    
    def deploy_docker(self):
        client = docker.from_env()
        client.images.build(path='.', tag='iron-condor:latest')
        container = client.containers.run(
            'iron-condor:latest',
            detach=True,
            environment={'ENV': self.environment},
            network='trading-net'
        )
        return container.id
    
    def deploy_kubernetes(self):
        config.load_kube_config()
        api = client.AppsV1Api()
        
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(name="iron-condor"),
            spec=client.V1DeploymentSpec(
                replicas=3,
                selector=client.V1LabelSelector(
                    match_labels={"app": "iron-condor"}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": "iron-condor"}
                    ),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="iron-condor",
                                image="iron-condor:latest",
                                env=[
                                    client.V1EnvVar(
                                        name="ENV",
                                        value=self.environment
                                    )
                                ]
                            )
                        ]
                    )
                )
            )
        )
        
        api.create_namespaced_deployment(
            namespace="trading", body=deployment)