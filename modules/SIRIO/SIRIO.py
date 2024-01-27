import re
import math
import gensim
import traceback
import numpy as np

from sqlalchemy import and_
from hera import Session, create
from hera.enum import CategoryType
from hera.schema import Event, EventCategorization, Category

from progress import progress_decorator

# TODO: Elimina la categoria stringa vuota dagli eventi

categorie = {}
swag_category = ['Divertimento', 'Discoteca', 'Sballo']


def load_model():
    model = gensim.models.fasttext.load_facebook_vectors('cc.it.300.bin')
    print('Caricato il modello cc.it.300.bin')

    db_categories = [category.name for category in get_categories()]
    categories = swag_category + list(set(db_categories) - set(swag_category))
    for category in categories :
        categorie[category] = model.get_vector(category)
    print(f"Creati i vettori delle categorie!\n{categories}")
    return model


def cosine_similarity(embeddingA, embeddingB):
    dot_product = np.dot(embeddingA, embeddingB)
    norm_embedding1 = np.linalg.norm(embeddingA, axis = 1)
    norm_embedding2 = np.linalg.norm(embeddingB)
    cosine_similarity = dot_product / (norm_embedding1 * norm_embedding2)
    index = np.argmax(cosine_similarity)
    return cosine_similarity[index]


def classify(model, sentence):
    embedding = [model.get_vector(word) for word in sentence.split()]
    similarities = []
    for categoria, embedding_categoria in categorie.items():
        similarities.append((categoria, cosine_similarity(embedding, embedding_categoria)))
    return sorted(similarities, key = lambda x: x[1], reverse = True)


def special_characters_handler(str):
    return re.sub(r'[^a-zA-Z0-9\s]', '', str)


@progress_decorator
def classify_event(evento: Event, model):
    classifications = classify(model, special_characters_handler(f"{evento['nome']} - {evento['descrizione']}"))
    classifications = [classification for classification in classifications if not math.isnan(classification[1])]
    print(classifications)
    new_list = []
    for sublist in classifications:
        if sublist[0] in swag_category:
            save_categorizzation(sublist, evento['id'])
            new_list.append(sublist)
    """     
    if evento['only_swag'] == 1 :
        sorted_list = sorted(
            list(filter(lambda x: x[1] > 0.35, [c for c in classifications if c not in new_list])),
                key = lambda x: x[1], reverse = True)
        if len(sorted_list) > 0 :
            save_categorizzation(sorted_list[0], evento['id'])
        if len(sorted_list) > 1 :
            save_categorizzation(sorted_list[1], evento['id'])
    else :
        executeSpecificQuery('DeleteNeededSirio', [evento['id']]) 
    """
    sorted_list = sorted(
        list(filter(lambda x: x[1] > 0.35, [c for c in classifications if c not in new_list])),
            key = lambda x: x[1], reverse = True)
    if len(sorted_list) > 0 :
        save_categorizzation(sorted_list[0], evento)
    if len(sorted_list) > 1 :
        save_categorizzation(sorted_list[1], evento)


def startSirio() -> int:
    try:
        model = load_model()
        events = get_events_without_sirio_categories()
        classify_event(events, 'SIRIO', model)
    except Exception as e:
        traceback.print_exception(e)
        return 1
    return 0


def get_events_without_sirio_categories() -> list[Event]:
    with Session() as session:
        return session.query(Event).outerjoin(
            EventCategorization, Event.id == EventCategorization.event_id
        ).outerjoin(
            Category, and_(
                Category.id == EventCategorization.category_id, 
                Category.type == CategoryType.SIRIO
            )
        ).filter(
            EventCategorization.id.is_(None)
        ).all()


def save_categorizzation(list: list, event: Event):
    with Session() as session:
        category = session.query(Category).filter(and_(
            Category.type.in_([CategoryType.SIRIO, CategoryType.SWAG]),
            Category.name == list[0]
        )).first()
        create(EventCategorization, {
            'category_id': category.id,
            'event_id': event.id,
            'similar': list[1]})


def get_categories() -> list[Category]:
    with Session() as session:
        return session.query(Category).filter(
            Category.type.in_([CategoryType.SIRIO, CategoryType.SWAG])
        ).all()
