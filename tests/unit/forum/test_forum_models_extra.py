# testes novos pro forum/models.py (projeto final ES2 - parte 1)
from datetime import timedelta

import pytest
from werkzeug.exceptions import NotFound

from flaskbb.forum.models import Forum, Post, Topic
from flaskbb.utils.settings import flaskbb_config


def test_topic_init_com_user(default_settings, user):
    topic = Topic(title="Meu topico", user=user)

    assert topic.user_id == user.id
    assert topic.username == user.username


def test_topic_init_com_content():
    # quando passa o content o Topic já cria o primeiro post
    topic = Topic(title="Meu topico", content="Conteudo do primeiro post")

    assert topic._post.content == "Conteudo do primeiro post"


def test_topic_init_sem_argumentos():
    # sem nada não pode dar erro, e as duas datas têm que ser iguais
    topic = Topic()

    assert topic.date_created == topic.last_updated


def test_is_first_post_verdadeiro(topic):
    assert topic.is_first_post(topic.first_post)


def test_is_first_post_falso(topic):
    # post que acabou de ser criado ainda não tem id
    outro_post = Post(content="Outro post")

    assert not topic.is_first_post(outro_post)


def test_get_topic_existente(topic):
    assert Topic.get_topic(topic.id) == topic


def test_get_topic_inexistente_da_404(default_settings):
    with pytest.raises(NotFound):
        Topic.get_topic(9999)


def test_get_forum_inexistente_da_404_logado(default_settings, user):
    with pytest.raises(NotFound):
        Forum.get_forum(9999, user)


def test_get_forum_inexistente_da_404_guest(default_settings, guest):
    with pytest.raises(NotFound):
        Forum.get_forum(9999, guest)


# tarefa 1.4 - teste parametrizado
# os dois últimos são títulos inválidos, só com pontuação, e o slug fica vazio
@pytest.mark.parametrize(
    "titulo, slug_esperado",
    [
        ("Ola Mundo", "ola-mundo"),
        ("Ação é legal", "acao-e-legal"),
        ("  Muitos   espacos  ", "muitos-espacos"),
        ("Topico 123", "topico-123"),
        ("!!!", ""),
        ("???", ""),
    ],
)
def test_topic_slug_parametrizado(titulo, slug_esperado):
    topic = Topic(title=titulo)

    assert topic.slug == slug_esperado


# tarefa 1.5 - teste com mock
# troca o time_utcnow do models por um mock pra controlar o "agora"
def test_tracker_needs_update_topico_antigo(topic, mocker):
    flaskbb_config["TRACKER_LENGTH"] = 1
    agora_falso = topic.last_post.date_created + timedelta(days=30)
    mock_agora = mocker.patch(
        "flaskbb.forum.models.time_utcnow", return_value=agora_falso
    )

    # o último post tem 30 dias e o tracker só olha 1 dia, então não precisa atualizar
    assert topic.tracker_needs_update(None, None) is False
    mock_agora.assert_called_once_with()


def test_tracker_needs_update_topico_recente(topic, mocker):
    flaskbb_config["TRACKER_LENGTH"] = 1
    agora_falso = topic.last_post.date_created + timedelta(hours=1)
    mock_agora = mocker.patch(
        "flaskbb.forum.models.time_utcnow", return_value=agora_falso
    )

    # post de 1 hora atrás e ninguém leu ainda, então tem que atualizar
    assert topic.tracker_needs_update(None, None) is True
    mock_agora.assert_called_once_with()
