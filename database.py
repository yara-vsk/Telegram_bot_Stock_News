from sqlalchemy import create_engine, sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, BigInteger, ForeignKey
from datetime import datetime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import Table


Base= declarative_base()

association_table = Table('association', Base.metadata,
    Column('bankier_id', Integer, ForeignKey('companies.id')),
    Column('users_id', Integer, ForeignKey('users.id'))
)

class Company(Base):
    __tablename__='companies'
    id = Column(Integer, primary_key=True)
    name_company = Column(String)
    url_page = Column(String)
    href_last_news = Column(String)
    href_last_communicate = Column(String)
    users = relationship("User",secondary=association_table, back_populates="companies")


class User(Base):
    __tablename__='users'
    id = Column(Integer, primary_key=True)
    id_telegram = Column(BigInteger)
    name_telegram = Column(String)
    companies = relationship("Company",secondary=association_table, back_populates="users")

class AllCompaniesGPW(Base):
    __tablename__='all_companies'
    id = Column(Integer, primary_key=True)
    name_company = Column(String)
    url_page = Column(String)

class AllCompaniesNC(Base):
    __tablename__='all_companies_nc'
    id = Column(Integer, primary_key=True)
    name_company = Column(String, unique=True)
    url_page = Column(String)


class DBcomand:
    def __init__(self):
        self.engine = create_engine('sqlite:///bankier.db?check_same_thread=False')
        session = sessionmaker(bind=self.engine)
        self.sess = session()

    def on_start_up(self):
        Base.metadata.create_all(self.engine)

    def create_user(self, id_telegram, name_telegram):
        old_user = self.sess.query(User).filter(User.id_telegram==id_telegram).first()
        if old_user != None:
            return old_user
        user = User(id_telegram=id_telegram, name_telegram=name_telegram)
        self.sess.add(user)
        self.sess.commit()
        return user

    def create_company(self,name_company,url_page,href_last_news,href_last_communicate):
        old_company=self.sess.query(Company).filter(Company.url_page==url_page).first()
        if old_company != None:
            return old_company
        company=Company(name_company=name_company,url_page=url_page,href_last_news=href_last_news,href_last_communicate=href_last_communicate)
        self.sess.add(company)
        self.sess.commit()
        return company

    def add_company_for_user(self,id_telegram, name_company,url_page,href_last_news,href_last_communicate):
        company=self.create_company(name_company=name_company,url_page=url_page,href_last_news=href_last_news,href_last_communicate=href_last_communicate)
        user=self.sess.query(User).filter(User.id_telegram==id_telegram).first()
        user.companies.append(company)
        self.sess.add(user)
        self.sess.commit()

    def delete_company_for_user(self,id_telegram, name_company):
        company=self.sess.query(Company).filter(Company.name_company==name_company).first()
        user=self.sess.query(User).filter(User.id_telegram==id_telegram).first()
        user.companies.remove(company)
        if not company.users:
            self.sess.execute(f"DELETE FROM companies WHERE id = {company.id}")
        #self.sess.add(user)
        self.sess.commit()

    def company_all_users(self,id_company):
        company = self.sess.query(Company).filter(Company.id_company == id_company).first()
        users=company.users
        list_users = []
        for user in users:
            list_users.append(int(user.id_telegam))
        return list_users

    def user_all_companies(self,id_telegram):
        user = self.sess.query(User).filter(User.id_telegram == id_telegram).first()
        companies = user.companies
        list_companies=[]
        for company in companies:
            list_companies.append(company.name_company)
        return list_companies

    def all_companies(self):
        return self.sess.query(Company).all()

    def update_href_last_for_company(self,id_company,href_last_news=None,href_last_communicate=None):
        company = self.sess.query(Company).filter(Company.id == id_company).first()
        if href_last_news != None:
            company.href_last_news=href_last_news
            self.sess.commit()
        if href_last_communicate != None:
            company.href_last_communicate=href_last_communicate
            self.sess.commit()

    def return_company(self,name_company):
        return self.sess.query(Company).filter(Company.name_company == name_company).first()

    def save_to_all_companies_gpw(self,name_company,url_company):
        company=AllCompaniesGPW(name_company=name_company,url_page=url_company)
        self.sess.add(company)
        self.sess.commit()

    def save_to_all_companies_nc(self,name_company,url_company):
        company=AllCompaniesNC(name_company=name_company,url_page=url_company)
        self.sess.add(company)
        self.sess.commit()

    def all_companies_gpw_actualization(self):
        if self.sess.query(AllCompaniesGPW).all():
            self.sess.execute("DELETE FROM all_companies")

    def all_companies_gpw(self):
        list_companies_name=[]
        for company in self.sess.query(AllCompaniesGPW).all():
            list_companies_name.append(company.name_company[0])
        list_companies = sorted(list(set(list_companies_name)))
        return list_companies

    def all_companies_gpw_for_character(self,character_user):
        list_companies_name=[]
        for company in self.sess.query(AllCompaniesGPW).all():
            if company.name_company[0]==character_user:
                list_companies_name.append(company.name_company)
        return list_companies_name


    def return_url_for_company_gpw(self,name_company):
        company= self.sess.query(AllCompaniesGPW).filter(
            AllCompaniesGPW.name_company == name_company).first()
        return company.url_page

    def count_users(self):
        return len(self.sess.query(User).all())






