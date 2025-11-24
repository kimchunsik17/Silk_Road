from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Caravan, CaravanImage, Reservation, Payment, 
    Review, Chat, BlockedPeriod
)

# 1. Custom User Admin
# ==============================================================================
class CustomUserAdmin(UserAdmin):
    """
    기존 UserAdmin을 확장하여 커스텀 필드를 관리자 페이지에 추가합니다.
    """
    model = User
    # 사용자 목록에 표시할 필드
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'user_type', 'is_verified')
    # 필터링 옵션 추가
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active', 'groups')
    
    # 사용자 수정 페이지의 필드 구성
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'contact')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        # 커스텀 필드 추가
        ('Custom Fields', {'fields': ('user_type', 'is_verified')}),
    )

# 2. Caravan Admin with Inlines
# ==============================================================================
class CaravanImageInline(admin.TabularInline):
    """
    Caravan 페이지에서 이미지를 함께 관리하기 위한 인라인입니다.
    TabularInline은 테이블 형태로 보여줍니다.
    """
    model = CaravanImage
    extra = 1  # 기본으로 보여줄 추가 이미지 폼의 수
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="150" />')
        return "(No image)"
    image_preview.short_description = 'Image Preview'


class BlockedPeriodInline(admin.TabularInline):
    """
    Caravan 페이지에서 예약 불가 기간을 설정하기 위한 인라인입니다.
    """
    model = BlockedPeriod
    extra = 1

class CaravanAdmin(admin.ModelAdmin):
    """
    Caravan 모델의 관리자 페이지를 커스터마이징합니다.
    """
    inlines = [CaravanImageInline, BlockedPeriodInline]
    list_display = ('name', 'host', 'status', 'capacity', 'location', 'created_at')
    list_filter = ('status', 'location', 'host__username')
    search_fields = ('name', 'description', 'host__username')
    readonly_fields = ('created_at', 'updated_at')
    
    # 필드를 논리적 그룹으로 묶어서 보여줍니다.
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'host', 'description', 'location')
        }),
        ('Details', {
            'fields': ('status', 'capacity', 'amenities')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

# 3. Reservation Admin
# ==============================================================================
class ReservationAdmin(admin.ModelAdmin):
    """
    Reservation 모델의 관리자 페이지를 커스터마이징합니다.
    """
    list_display = ('id', 'caravan', 'guest', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('caravan__name', 'guest__username')
    autocomplete_fields = ['guest', 'caravan']  # ForeignKey 필드를 검색 가능한 드롭다운으로 변경

# 4. Review Admin
# ==============================================================================
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'reservation', 'reviewer', 'target_user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'reviewer__username', 'target_user__username')
    autocomplete_fields = ['reservation', 'reviewer', 'target_user']

# 5. Payment Admin
# ==============================================================================
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'reservation_id', 'amount', 'status', 'paid_at')
    list_filter = ('status',)
    search_fields = ('reservation__id',)

    def reservation_id(self, obj):
        return obj.reservation.id
    reservation_id.short_description = 'Reservation ID'

# 6. Chat Admin
# ==============================================================================
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'message')
    autocomplete_fields = ['sender', 'receiver']


# Register all models with their custom admins
# ==============================================================================
admin.site.register(User, CustomUserAdmin)
admin.site.register(Caravan, CaravanAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Chat, ChatAdmin)
# BlockedPeriod는 CaravanAdmin에 인라인으로 포함되지만, 별도로도 관리할 수 있도록 등록합니다.
admin.site.register(BlockedPeriod) 
admin.site.register(CaravanImage)

admin.site.site_header = "Silk Road Admin"
admin.site.site_title = "Silk Road Admin Portal"
admin.site.index_title = "Welcome to Silk Road Administration"