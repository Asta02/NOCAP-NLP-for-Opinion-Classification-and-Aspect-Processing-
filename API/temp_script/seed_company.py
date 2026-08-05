from services.company_service import (
    get_company_service,
)


def main():

    service = get_company_service()

    company = service.create_company(

        company_name="Demo Company",

        industry="Technology",

        email="demo@example.com",

        username="demo",

        password="demo123",

    )

    print(
        f"Created company id={company.id}",
    )


if __name__ == "__main__":
    main()