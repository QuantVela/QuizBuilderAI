from langchain.document_loaders import MastodonTootsLoader

def process_mastodon():
    loader = MastodonTootsLoader(
        mastodon_accounts=["@Gargron@mastodon.social"],
        number_toots=100, 
    )
    documents = loader.load()

