
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from scanner.models import ScanHistory
from scanner.validation import validate_url
from scanner.services import scan_url
from django.utils import timezone
from django.views.decorators.http import require_GET

def scan(request):
    return render(request, 'scanner/scan.html')


@require_POST
def scan_api(request):
    url = request.POST.get("url", "")

    # URL Validation
    is_valid, message = validate_url(url)

    if not is_valid:
        return JsonResponse({
            "success": False,
            "message": message
        }, status=400)

    # ML Model Prediction
    try:
        result = scan_url(url.strip())

        if request.user.is_authenticated:
            ScanHistory.objects.create(
                user=request.user,
                url=url.strip(),
                prediction=result['prediction'],
                phishing_probability=result['phishing_probability']
            )

        return JsonResponse({
            "success": True,
            "message": "URL scanned successfully.",
            "result": result
        })

    except Exception:
        return JsonResponse({
            "success": False,
            "message": "Something went wrong while scanning. Please try again."
        }, status=500)


@login_required
@require_GET
def scan_history_api(request):

    scans = ScanHistory.objects.filter(
        user=request.user
    ).order_by('-scanned_at')

    scan_data = [
        {
            'id': scan.id,
            'url': scan.url,
            'prediction': scan.prediction,
            'phishing_probability': scan.phishing_probability,
            'scanned_at': timezone.localtime(
                scan.scanned_at
            ).strftime('%b %d, %Y %I:%M %p')
        }
        for scan in scans
    ]

    return JsonResponse({
        'status': 'success',
        'total_count': len(scan_data),
        'scans': scan_data
    })

@login_required
def scan_history(request):
    return render(request, 'scanner/history.html')