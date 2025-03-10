import pytest

import python_on_whales
from python_on_whales import DockerClient, DockerException
from python_on_whales.utils import PROJECT_ROOT

pytestmark = pytest.mark.skipif(
    not python_on_whales.docker.compose.is_installed(),
    reason="Those tests need docker compose.",
)

docker = DockerClient(
    compose_files=[PROJECT_ROOT / "tests/python_on_whales/components/dummy_compose.yml"]
)


def test_docker_compose_build():
    docker.compose.build()
    docker.compose.build(["my_service"])
    docker.image.remove("some_random_image")


def test_docker_compose_up_down():
    docker = DockerClient(
        compose_files=[
            PROJECT_ROOT
            / "tests/python_on_whales/components/dummy_compose_ends_quickly.yml"
        ]
    )
    docker.compose.up(["busybox", "alpine"])


def test_no_containers():
    assert docker.compose.ps() == []


def test_docker_compose_up_detach_down():
    docker.compose.up(detach=True)
    docker.compose.down()


def test_docker_compose_up_build():
    docker.compose.up(build=True, detach=True)
    with docker.image.inspect("some_random_image"):
        docker.compose.down()


def test_docker_compose_up_down_some_services():
    docker.compose.up(["my_service", "busybox"], detach=True)
    docker.compose.down()


def test_docker_compose_ps():
    docker.compose.up(["my_service", "busybox"], detach=True)
    containers = docker.compose.ps()
    names = set(x.name for x in containers)
    assert names == {"components_my_service_1", "components_busybox_1"}
    docker.compose.down()


@pytest.mark.skipif(
    True,
    reason="TODO: Fixme. For some reason it works locally but not in "
    "the CI. We get a .dockercfg: $HOME is not defined.",
)
def test_docker_compose_pull():
    try:
        docker.image.remove("busybox")
    except DockerException:
        pass
    try:
        docker.image.remove("alpine")
    except DockerException:
        pass
    docker.compose.pull(["busybox", "alpine"])
    docker.image.inspect(["busybox", "alpine"])
