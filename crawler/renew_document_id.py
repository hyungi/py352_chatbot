from crawler.models import DocumentSummary, PoliticsDocument, ITScienceDocument, CultureLivingDocument, EconomicsDocument, SocietyDocument, WorldDocument


def renew_document_id():
    document_id_instance = DocumentSummary.objects.all()

    for i in range(len(document_id_instance)):
        if PoliticsDocument.objects.filter(document_id=document_id_instance[i].document_id).exists():
            document_id_instance[i].date = PoliticsDocument.objects.get(document_id=document_id_instance[i].document_id).published_date
        elif ITScienceDocument.objects.filter(document_id=document_id_instance[i].document_id).exists():
            document_id_instance[i].date = ITScienceDocument.objects.get(document_id=document_id_instance[i].document_id).published_date
        elif CultureLivingDocument.objects.filter(document_id=document_id_instance[i].document_id).exists():
            document_id_instance[i].date = CultureLivingDocument.objects.get(document_id=document_id_instance[i].document_id).published_date
        elif EconomicsDocument.objects.filter(document_id=document_id_instance[i].document_id).exists():
            document_id_instance[i].date = EconomicsDocument.objects.get(document_id=document_id_instance[i].document_id).published_date
        elif SocietyDocument.objects.filter(document_id=document_id_instance[i].document_id).exists():
            document_id_instance[i].date = SocietyDocument.objects.get(document_id=document_id_instance[i].document_id).published_date
        elif WorldDocument.objects.filter(document_id=document_id_instance[i].document_id).exists():
            document_id_instance[i].date = WorldDocument.objects.get(document_id=document_id_instance[i].document_id).published_date

        document_id_instance[i].save()
