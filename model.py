import tensorflow as tf
from tensorflow.keras import layers, Model


def build_model(vocab_size, embedding_dim=128):
    input_target = layers.Input((1,))
    input_context = layers.Input((1,))

    embedding_layer = layers.Embedding(vocab_size, embedding_dim, name="emb")

    target_emb = embedding_layer(input_target)
    context_emb = embedding_layer(input_context)

    # убираем лишние измерения
    target_emb = layers.Flatten()(target_emb)
    context_emb = layers.Flatten()(context_emb)

    dot = layers.Dot(axes=1)([target_emb, context_emb])

    output = layers.Activation("sigmoid")(dot)

    model = Model([input_target, input_context], output)
    model.compile(optimizer="adam", loss="binary_crossentropy")

    return model