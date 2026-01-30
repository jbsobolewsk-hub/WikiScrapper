# wiki/client.py

from abc import ABC, abstractmethod

from bs4 import BeautifulSoup


class WikiClient(ABC):

    @abstractmethod
    def get_summary(self, phrase: str) -> str:
        pass

    @abstractmethod
    def get_page_text(self, phrase: str) -> str:
        pass

    @abstractmethod
    def get_tables(self, phrase: str) -> list[str]:
        pass

    @abstractmethod
    def get_links(self, phrase: str) -> list[str]:
        pass

    @abstractmethod
    def search(self, phrase: str) -> BeautifulSoup:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
