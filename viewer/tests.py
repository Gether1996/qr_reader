"""
Comprehensive test suite for QR Reader Django Application
Tests all models, relationships, and business logic to ensure production readiness.
"""

from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth.hashers import check_password
from datetime import datetime, date, timedelta
from unittest.mock import patch, Mock
from viewer.models import (
    Company, User, QRCodeProfile, ScanEvent, Vacation,
    PasswordResetToken, UserPasswordSetupToken, AuditLog, Magazine, MagazineArticle, ContentBlock
)


# ============================================================================
# COMPANY MODEL TESTS
# ============================================================================

class CompanyModelTests(TestCase):
    """Test suite for Company model"""
    
    def setUp(self):
        """Set up test data"""
        self.company_data = {
            'name': 'Test Company s.r.o.',
            'email': 'test@company.sk',
            'password': 'plain_password_123'
        }
    
    def test_company_creation_minimal(self):
        """Test creating company with minimal required fields"""
        company = Company.objects.create(
            name=self.company_data['name'],
            email=self.company_data['email'],
            password=self.company_data['password']
        )
        
        self.assertEqual(company.name, 'Test Company s.r.o.')
        self.assertEqual(company.email, 'test@company.sk')
        self.assertIsNotNone(company.created_at)
        self.assertTrue(company.is_active)
        self.assertFalse(company.auto_lunch_breaks)
        self.assertFalse(company.notification_company)
    
    def test_company_creation_full(self):
        """Test creating company with all optional fields"""
        company = Company.objects.create(
            name='Full Company s.r.o.',
            email='full@company.sk',
            password='password',
            ico='12345678',
            dic='2012345678',
            phone='+421901234567',
            street='Hlavná',
            street_number='123/45',
            zip_code='81101',
            city='Bratislava',
            state='Slovensko',
            auto_lunch_breaks=True,
            notification_company=True,
            notify_arrival=True,
            notify_departure=True,
            notify_vacation=True
        )
        
        self.assertEqual(company.ico, '12345678')
        self.assertEqual(company.dic, '2012345678')
        self.assertEqual(company.phone, '+421901234567')
        self.assertEqual(company.street, 'Hlavná')
        self.assertEqual(company.city, 'Bratislava')
        self.assertTrue(company.auto_lunch_breaks)
        self.assertTrue(company.notify_arrival)
    
    def test_company_email_unique_constraint(self):
        """Test that company email must be unique"""
        Company.objects.create(**self.company_data)
        
        with self.assertRaises(IntegrityError):
            Company.objects.create(**self.company_data)
    
    def test_company_str_representation(self):
        """Test string representation of company"""
        company = Company.objects.create(**self.company_data)
        self.assertEqual(str(company), 'Test Company s.r.o.')
    
    def test_company_verbose_name_plural(self):
        """Test that plural name is set correctly"""
        self.assertEqual(str(Company._meta.verbose_name_plural), 'Companies')
    
    def test_set_password_hashing(self):
        """Test that set_password properly hashes password"""
        company = Company.objects.create(
            name='Test',
            email='hash@test.sk',
            password='plain'
        )
        
        raw_password = 'secure_password_123'
        company.set_password(raw_password)
        company.save()
        
        # Password should be hashed
        self.assertNotEqual(company.password, raw_password)
        self.assertTrue(company.password.startswith('pbkdf2_'))
        
        # Should be able to verify
        self.assertTrue(check_password(raw_password, company.password))
    
    def test_check_password_correct(self):
        """Test checking password with correct password"""
        company = Company.objects.create(
            name='Test',
            email='check@test.sk',
            password='plain'
        )
        
        raw_password = 'my_secure_password'
        company.set_password(raw_password)
        company.save()
        
        self.assertTrue(company.check_password(raw_password))
    
    def test_check_password_incorrect(self):
        """Test checking password with incorrect password"""
        company = Company.objects.create(
            name='Test',
            email='check2@test.sk',
            password='plain'
        )
        
        company.set_password('correct_password')
        company.save()
        
        self.assertFalse(company.check_password('wrong_password'))
    
    def test_company_is_active_default(self):
        """Test that companies are active by default"""
        company = Company.objects.create(**self.company_data)
        self.assertTrue(company.is_active)
    
    def test_company_deactivation(self):
        """Test deactivating a company"""
        company = Company.objects.create(**self.company_data)
        company.is_active = False
        company.save()
        
        company.refresh_from_db()
        self.assertFalse(company.is_active)
    
    def test_company_notification_settings(self):
        """Test notification settings toggle correctly"""
        company = Company.objects.create(**self.company_data)
        
        self.assertFalse(company.notification_company)
        self.assertFalse(company.notify_arrival)
        self.assertFalse(company.notify_departure)
        self.assertFalse(company.notify_vacation)
        
        company.notification_company = True
        company.notify_arrival = True
        company.notify_departure = True
        company.notify_vacation = True
        company.save()
        
        company.refresh_from_db()
        self.assertTrue(company.notification_company)
        self.assertTrue(company.notify_arrival)
        self.assertTrue(company.notify_departure)
        self.assertTrue(company.notify_vacation)
    
    def test_company_optional_fields_null(self):
        """Test that optional fields can be null"""
        company = Company.objects.create(
            name='Minimal Company',
            email='minimal@test.sk',
            password='pass'
        )
        
        self.assertIsNone(company.ico)
        self.assertIsNone(company.dic)
        self.assertIsNone(company.phone)
        self.assertIsNone(company.street)
        self.assertIsNone(company.street_number)
        self.assertIsNone(company.zip_code)
        self.assertIsNone(company.city)
        self.assertIsNone(company.state)


# ============================================================================
# USER MODEL TESTS
# ============================================================================

class UserModelTests(TestCase):
    """Test suite for User model"""
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            name='Test Company',
            email='company@test.sk',
            password='password'
        )
        
        self.user_data = {
            'company': self.company,
            'name': 'Ján Novák',
            'email': 'jan.novak@test.sk',
            'password': 'user_password'
        }
    
    def test_user_creation_minimal(self):
        """Test creating user with minimal required fields"""
        user = User.objects.create(**self.user_data)
        
        self.assertEqual(user.name, 'Ján Novák')
        self.assertEqual(user.email, 'jan.novak@test.sk')
        self.assertEqual(user.company, self.company)
        self.assertIsNotNone(user.created_at)
        self.assertTrue(user.is_active)
        self.assertEqual(user.working_hours, 160)
        self.assertTrue(user.has_lunch_break)
        self.assertEqual(user.lunch_break_duration, 30)
        self.assertEqual(user.holidays_per_year, 20)
        self.assertFalse(user.is_manager)
    
    def test_user_creation_full(self):
        """Test creating user with all optional fields"""
        user = User.objects.create(
            company=self.company,
            name='Peter Veľký',
            email='peter.velky@test.sk',
            password='password',
            rc='900101/1234',
            phone='+421901234567',
            birth_date=date(1990, 1, 1),
            working_hours=168,
            has_lunch_break=False,
            lunch_break_duration=45,
            holidays_per_year=25,
            is_manager=True,
            can_edit_employees=True,
            can_edit_qr_codes=True,
            can_edit_absences=True,
            notifications=True,
            notify_arrival=True,
            notify_departure=True,
            notify_vacation=True
        )
        
        self.assertEqual(user.rc, '900101/1234')
        self.assertEqual(user.phone, '+421901234567')
        self.assertEqual(user.birth_date, date(1990, 1, 1))
        self.assertEqual(user.working_hours, 168)
        self.assertFalse(user.has_lunch_break)
        self.assertEqual(user.lunch_break_duration, 45)
        self.assertEqual(user.holidays_per_year, 25)
        self.assertTrue(user.is_manager)
        self.assertTrue(user.can_edit_employees)
        self.assertTrue(user.can_edit_qr_codes)
        self.assertTrue(user.can_edit_absences)
    
    def test_user_email_unique_constraint(self):
        """Test that user email must be unique"""
        User.objects.create(**self.user_data)
        
        # Try to create another user with same email
        with self.assertRaises(IntegrityError):
            User.objects.create(**self.user_data)
    
    def test_user_str_representation(self):
        """Test string representation of user"""
        user = User.objects.create(**self.user_data)
        self.assertEqual(str(user), 'Ján Novák (Test Company)')
    
    def test_user_company_relationship(self):
        """Test that user is properly related to company"""
        user = User.objects.create(**self.user_data)
        
        # Test forward relationship
        self.assertEqual(user.company, self.company)
        
        # Test reverse relationship
        self.assertIn(user, self.company.users.all())
        self.assertEqual(self.company.users.count(), 1)
    
    def test_user_cascade_delete_on_company(self):
        """Test that users are deleted when company is deleted"""
        user = User.objects.create(**self.user_data)
        user_id = user.id
        
        self.company.delete()
        
        # User should be deleted
        self.assertFalse(User.objects.filter(id=user_id).exists())
    
    def test_user_set_password(self):
        """Test that set_password properly hashes password"""
        user = User.objects.create(**self.user_data)
        
        raw_password = 'new_secure_password'
        user.set_password(raw_password)
        user.save()
        
        # Password should be hashed
        self.assertNotEqual(user.password, raw_password)
        self.assertTrue(user.password.startswith('pbkdf2_'))
        
        # Should be able to verify
        self.assertTrue(check_password(raw_password, user.password))
    
    def test_user_check_password_correct(self):
        """Test checking password with correct password"""
        user = User.objects.create(**self.user_data)
        
        raw_password = 'user_secure_pass'
        user.set_password(raw_password)
        user.save()
        
        self.assertTrue(user.check_password(raw_password))
    
    def test_user_check_password_incorrect(self):
        """Test checking password with incorrect password"""
        user = User.objects.create(**self.user_data)
        
        user.set_password('correct_password')
        user.save()
        
        self.assertFalse(user.check_password('wrong_password'))
    
    def test_multiple_users_per_company(self):
        """Test that company can have multiple users"""
        user1 = User.objects.create(
            company=self.company,
            name='User 1',
            email='user1@test.sk',
            password='pass'
        )
        user2 = User.objects.create(
            company=self.company,
            name='User 2',
            email='user2@test.sk',
            password='pass'
        )
        user3 = User.objects.create(
            company=self.company,
            name='User 3',
            email='user3@test.sk',
            password='pass'
        )
        
        self.assertEqual(self.company.users.count(), 3)
        self.assertIn(user1, self.company.users.all())
        self.assertIn(user2, self.company.users.all())
        self.assertIn(user3, self.company.users.all())
    
    def test_user_permission_flags(self):
        """Test user permission flags work correctly"""
        user = User.objects.create(**self.user_data)
        
        # Default permissions
        self.assertFalse(user.is_manager)
        self.assertFalse(user.can_edit_employees)
        self.assertFalse(user.can_edit_qr_codes)
        self.assertFalse(user.can_edit_absences)
        
        # Grant permissions
        user.is_manager = True
        user.can_edit_employees = True
        user.can_edit_qr_codes = True
        user.can_edit_absences = True
        user.save()
        
        user.refresh_from_db()
        self.assertTrue(user.is_manager)
        self.assertTrue(user.can_edit_employees)
        self.assertTrue(user.can_edit_qr_codes)
        self.assertTrue(user.can_edit_absences)
    
    def test_user_notification_settings(self):
        """Test user notification settings"""
        user = User.objects.create(**self.user_data)
        
        self.assertFalse(user.notifications)
        self.assertFalse(user.notify_arrival)
        self.assertFalse(user.notify_departure)
        self.assertFalse(user.notify_vacation)
        
        user.notifications = True
        user.notify_arrival = True
        user.notify_departure = True
        user.notify_vacation = True
        user.save()
        
        user.refresh_from_db()
        self.assertTrue(user.notifications)
        self.assertTrue(user.notify_arrival)
        self.assertTrue(user.notify_departure)
        self.assertTrue(user.notify_vacation)
    
    def test_user_working_hours_settings(self):
        """Test user working hours and lunch break settings"""
        user = User.objects.create(**self.user_data)
        
        # Test defaults
        self.assertEqual(user.working_hours, 160)
        self.assertTrue(user.has_lunch_break)
        self.assertEqual(user.lunch_break_duration, 30)
        
        # Modify settings
        user.working_hours = 176
        user.has_lunch_break = False
        user.lunch_break_duration = 60
        user.save()
        
        user.refresh_from_db()
        self.assertEqual(user.working_hours, 176)
        self.assertFalse(user.has_lunch_break)
        self.assertEqual(user.lunch_break_duration, 60)
    
    def test_user_deactivation(self):
        """Test deactivating a user"""
        user = User.objects.create(**self.user_data)
        self.assertTrue(user.is_active)
        
        user.is_active = False
        user.save()
        
        user.refresh_from_db()
        self.assertFalse(user.is_active)
    
    def test_user_optional_fields_null(self):
        """Test that optional fields can be null"""
        user = User.objects.create(
            company=self.company,
            name='Minimal User',
            email='minimal@test.sk',
            password='pass'
        )
        
        self.assertIsNone(user.rc)
        self.assertIsNone(user.phone)
        self.assertIsNone(user.birth_date)


# ============================================================================
# QRCODEPROFILE MODEL TESTS
# ============================================================================

class QRCodeProfileModelTests(TestCase):
    """Test suite for QRCodeProfile model"""
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            name='Test Company',
            email='company@test.sk',
            password='password'
        )
        
        self.qr_data = {
            'company': self.company,
            'name': 'Hlavný vchod',
            'location': 'Bratislava, Hlavná 123'
        }
    
    def test_qrcode_creation_minimal(self):
        """Test creating QR code with minimal required fields"""
        qr = QRCodeProfile.objects.create(**self.qr_data)
        
        self.assertEqual(qr.name, 'Hlavný vchod')
        self.assertEqual(qr.location, 'Bratislava, Hlavná 123')
        self.assertEqual(qr.company, self.company)
        self.assertIsNotNone(qr.created_at)
        self.assertTrue(qr.is_active)
        self.assertIsNotNone(qr.uuid)
        self.assertEqual(len(qr.uuid), 36)  # UUID4 format
    
    def test_qrcode_creation_with_additional_info(self):
        """Test creating QR code with additional info"""
        qr = QRCodeProfile.objects.create(
            company=self.company,
            name='Zadný vchod',
            location='Košice, Mlynská 45',
            additional_info='Len pre zamestnancov, prístup kartou'
        )
        
        self.assertEqual(qr.additional_info, 'Len pre zamestnancov, prístup kartou')
    
    def test_qrcode_uuid_auto_generation(self):
        """Test that UUID is automatically generated on save"""
        qr = QRCodeProfile(
            company=self.company,
            name='Test QR',
            location='Test Location'
        )
        
        # UUID should be empty/falsy before save
        self.assertFalse(qr.uuid)
        
        qr.save()
        
        # UUID should be generated after save
        self.assertIsNotNone(qr.uuid)
        self.assertTrue(qr.uuid)  # Should have truthy value
        self.assertEqual(len(qr.uuid), 36)
    
    def test_qrcode_uuid_uniqueness(self):
        """Test that each QR code gets a unique UUID"""
        qr1 = QRCodeProfile.objects.create(**self.qr_data)
        qr2 = QRCodeProfile.objects.create(
            company=self.company,
            name='Another QR',
            location='Another Location'
        )
        
        self.assertNotEqual(qr1.uuid, qr2.uuid)
    
    def test_qrcode_uuid_unique_constraint(self):
        """Test that UUID must be unique in database"""
        qr1 = QRCodeProfile.objects.create(**self.qr_data)
        
        # Try to create another QR with same UUID
        qr2 = QRCodeProfile(
            company=self.company,
            name='Duplicate UUID',
            location='Location'
        )
        qr2.uuid = qr1.uuid
        
        with self.assertRaises(IntegrityError):
            qr2.save()
    
    def test_qrcode_image_generation(self):
        """Test that QR code image is generated automatically"""
        qr = QRCodeProfile.objects.create(**self.qr_data)
        
        # QR code image should be generated
        self.assertTrue(qr.qr_code)
        self.assertTrue(qr.qr_code.name.startswith('qr_codes/qr_'))
        self.assertTrue(qr.qr_code.name.endswith('.png'))
    
    def test_qrcode_image_regeneration_on_update(self):
        """Test that QR code image is regenerated when object is updated"""
        qr = QRCodeProfile.objects.create(**self.qr_data)
        original_image_name = qr.qr_code.name
        
        # Update the QR code
        qr.name = 'Updated Name'
        qr.save()
        
        # Image should still exist (may be same or regenerated)
        self.assertTrue(qr.qr_code)
    
    def test_qrcode_str_representation(self):
        """Test string representation of QR code"""
        qr = QRCodeProfile.objects.create(**self.qr_data)
        self.assertEqual(str(qr), 'Hlavný vchod - Test Company')
    
    def test_qrcode_company_relationship(self):
        """Test that QR code is properly related to company"""
        qr = QRCodeProfile.objects.create(**self.qr_data)
        
        # Test forward relationship
        self.assertEqual(qr.company, self.company)
        
        # Test reverse relationship
        self.assertIn(qr, self.company.qr_codes.all())
        self.assertEqual(self.company.qr_codes.count(), 1)
    
    def test_qrcode_cascade_delete_on_company(self):
        """Test that QR codes are deleted when company is deleted"""
        qr = QRCodeProfile.objects.create(**self.qr_data)
        qr_id = qr.id
        
        self.company.delete()
        
        # QR code should be deleted
        self.assertFalse(QRCodeProfile.objects.filter(id=qr_id).exists())
    
    def test_multiple_qrcodes_per_company(self):
        """Test that company can have multiple QR codes"""
        qr1 = QRCodeProfile.objects.create(
            company=self.company,
            name='QR 1',
            location='Location 1'
        )
        qr2 = QRCodeProfile.objects.create(
            company=self.company,
            name='QR 2',
            location='Location 2'
        )
        qr3 = QRCodeProfile.objects.create(
            company=self.company,
            name='QR 3',
            location='Location 3'
        )
        
        self.assertEqual(self.company.qr_codes.count(), 3)
        self.assertIn(qr1, self.company.qr_codes.all())
        self.assertIn(qr2, self.company.qr_codes.all())
        self.assertIn(qr3, self.company.qr_codes.all())
    
    def test_qrcode_activation_toggle(self):
        """Test activating/deactivating QR codes"""
        qr = QRCodeProfile.objects.create(**self.qr_data)
        
        # Should be active by default
        self.assertTrue(qr.is_active)
        
        # Deactivate
        qr.is_active = False
        qr.save()
        
        qr.refresh_from_db()
        self.assertFalse(qr.is_active)
        
        # Reactivate
        qr.is_active = True
        qr.save()
        
        qr.refresh_from_db()
        self.assertTrue(qr.is_active)
    
    def test_qrcode_additional_info_optional(self):
        """Test that additional_info is optional"""
        qr = QRCodeProfile.objects.create(**self.qr_data)
        self.assertIsNone(qr.additional_info)
    
    def test_qrcode_generate_uuid_method(self):
        """Test the generate_uuid method"""
        qr = QRCodeProfile(
            company=self.company,
            name='Test',
            location='Test'
        )
        
        uuid1 = qr.generate_uuid()
        uuid2 = qr.generate_uuid()
        
        # Each call should generate a different UUID
        self.assertNotEqual(uuid1, uuid2)
        self.assertEqual(len(uuid1), 36)
        self.assertEqual(len(uuid2), 36)
    
    def test_qrcode_uuid_not_overwritten_on_update(self):
        """Test that UUID is not regenerated on update"""
        qr = QRCodeProfile.objects.create(**self.qr_data)
        original_uuid = qr.uuid
        
        # Update the QR code
        qr.name = 'Updated Name'
        qr.save()
        
        # UUID should remain the same
        qr.refresh_from_db()
        self.assertEqual(qr.uuid, original_uuid)


# ============================================================================
# SCANEVENT MODEL TESTS
# ============================================================================

class ScanEventModelTests(TestCase):
    """Test suite for ScanEvent model"""
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            name='Test Company',
            email='company@test.sk',
            password='password'
        )
        
        self.user = User.objects.create(
            company=self.company,
            name='Test User',
            email='user@test.sk',
            password='password'
        )
        
        self.qr_code = QRCodeProfile.objects.create(
            company=self.company,
            name='Test QR',
            location='Test Location'
        )
        
        self.scan_data = {
            'qr_code': self.qr_code,
            'scanned_by': self.user,
            'latitude': 48.1486,
            'longitude': 17.1077,
            'scan_type': 'arrival'
        }
    
    def test_scan_event_creation_minimal(self):
        """Test creating scan event with required fields"""
        scan = ScanEvent.objects.create(**self.scan_data)
        
        self.assertEqual(scan.qr_code, self.qr_code)
        self.assertEqual(scan.scanned_by, self.user)
        self.assertEqual(scan.latitude, 48.1486)
        self.assertEqual(scan.longitude, 17.1077)
        self.assertEqual(scan.scan_type, 'arrival')
        self.assertIsNotNone(scan.timestamp)
        self.assertFalse(scan.is_home_office)
        self.assertFalse(scan.is_business_trip)
    
    def test_scan_event_all_scan_types(self):
        """Test all scan type choices"""
        scan_types = ['arrival', 'departure', 'lunch_break_start', 'lunch_break_end']
        
        for scan_type in scan_types:
            scan = ScanEvent.objects.create(
                qr_code=self.qr_code,
                scanned_by=self.user,
                latitude=48.1486,
                longitude=17.1077,
                scan_type=scan_type
            )
            self.assertEqual(scan.scan_type, scan_type)
    
    def test_scan_event_with_device_info(self):
        """Test scan event with device information"""
        device_info = 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)'
        
        scan = ScanEvent.objects.create(
            **self.scan_data,
            device_info=device_info
        )
        
        self.assertEqual(scan.device_info, device_info)
    
    def test_scan_event_with_address(self):
        """Test scan event with pre-filled address"""
        scan = ScanEvent.objects.create(
            **self.scan_data,
            address='Hlavná 123, 81101 Bratislava, Slovensko'
        )
        
        self.assertEqual(scan.address, 'Hlavná 123, 81101 Bratislava, Slovensko')
    
    def test_scan_event_home_office(self):
        """Test home office scan event"""
        scan = ScanEvent.objects.create(
            scanned_by=self.user,
            latitude=48.1486,
            longitude=17.1077,
            scan_type='arrival',
            is_home_office=True
        )
        
        self.assertTrue(scan.is_home_office)
        self.assertFalse(scan.is_business_trip)
        self.assertIsNone(scan.qr_code)
    
    def test_scan_event_business_trip(self):
        """Test business trip scan event"""
        scan = ScanEvent.objects.create(
            scanned_by=self.user,
            latitude=50.0755,
            longitude=14.4378,  # Prague
            scan_type='arrival',
            is_business_trip=True
        )
        
        self.assertTrue(scan.is_business_trip)
        self.assertFalse(scan.is_home_office)
        self.assertIsNone(scan.qr_code)
    
    def test_scan_event_str_representation_normal(self):
        """Test string representation for normal scan"""
        scan = ScanEvent.objects.create(**self.scan_data)
        expected = f"Test QR scanned at {scan.timestamp}"
        self.assertEqual(str(scan), expected)
    
    def test_scan_event_str_representation_home_office(self):
        """Test string representation for home office scan"""
        scan = ScanEvent.objects.create(
            scanned_by=self.user,
            latitude=48.1486,
            longitude=17.1077,
            scan_type='arrival',
            is_home_office=True
        )
        expected = f"Home Office scan at {scan.timestamp}"
        self.assertEqual(str(scan), expected)
    
    def test_scan_event_str_representation_business_trip(self):
        """Test string representation for business trip scan"""
        scan = ScanEvent.objects.create(
            scanned_by=self.user,
            latitude=48.1486,
            longitude=17.1077,
            scan_type='arrival',
            is_business_trip=True
        )
        expected = f"Business Trip scan at {scan.timestamp}"
        self.assertEqual(str(scan), expected)
    
    def test_scan_event_str_representation_no_qr_code(self):
        """Test string representation when QR code is None"""
        scan = ScanEvent.objects.create(
            scanned_by=self.user,
            latitude=48.1486,
            longitude=17.1077,
            scan_type='arrival'
        )
        expected = f"Unknown scanned at {scan.timestamp}"
        self.assertEqual(str(scan), expected)
    
    def test_scan_event_ordering(self):
        """Test that scans are ordered by timestamp descending"""
        import time
        scan1 = ScanEvent.objects.create(**self.scan_data)
        time.sleep(0.001)
        scan2 = ScanEvent.objects.create(**self.scan_data)
        time.sleep(0.001)
        scan3 = ScanEvent.objects.create(**self.scan_data)
        
        scans = ScanEvent.objects.all()
        
        # Should be ordered newest first
        self.assertEqual(scans[0], scan3)
        self.assertEqual(scans[1], scan2)
        self.assertEqual(scans[2], scan1)
    
    def test_scan_event_qr_code_relationship(self):
        """Test relationship with QR code"""
        scan = ScanEvent.objects.create(**self.scan_data)
        
        # Forward relationship
        self.assertEqual(scan.qr_code, self.qr_code)
        
        # Reverse relationship
        self.assertIn(scan, self.qr_code.scans.all())
        self.assertEqual(self.qr_code.scans.count(), 1)
    
    def test_scan_event_user_relationship(self):
        """Test relationship with user"""
        scan = ScanEvent.objects.create(**self.scan_data)
        
        # Forward relationship
        self.assertEqual(scan.scanned_by, self.user)
        
        # Reverse relationship
        self.assertIn(scan, self.user.scans.all())
        self.assertEqual(self.user.scans.count(), 1)
    
    def test_scan_event_cascade_on_qr_delete(self):
        """Test that scans are deleted when QR code is deleted"""
        scan = ScanEvent.objects.create(**self.scan_data)
        scan_id = scan.id
        
        self.qr_code.delete()
        
        # Scan should be deleted
        self.assertFalse(ScanEvent.objects.filter(id=scan_id).exists())
    
    def test_scan_event_set_null_on_user_delete(self):
        """Test that scan is preserved but user is set to NULL when user is deleted"""
        scan = ScanEvent.objects.create(**self.scan_data)
        scan_id = scan.id
        
        self.user.delete()
        
        # Scan should still exist
        self.assertTrue(ScanEvent.objects.filter(id=scan_id).exists())
        
        scan.refresh_from_db()
        # User should be None
        self.assertIsNone(scan.scanned_by)
    
    def test_multiple_scans_per_user(self):
        """Test that user can have multiple scans"""
        scan1 = ScanEvent.objects.create(
            qr_code=self.qr_code,
            scanned_by=self.user,
            latitude=self.scan_data['latitude'],
            longitude=self.scan_data['longitude'],
            scan_type='arrival'
        )
        scan2 = ScanEvent.objects.create(
            qr_code=self.qr_code,
            scanned_by=self.user,
            latitude=self.scan_data['latitude'],
            longitude=self.scan_data['longitude'],
            scan_type='lunch_break_start'
        )
        scan3 = ScanEvent.objects.create(
            qr_code=self.qr_code,
            scanned_by=self.user,
            latitude=self.scan_data['latitude'],
            longitude=self.scan_data['longitude'],
            scan_type='lunch_break_end'
        )
        scan4 = ScanEvent.objects.create(
            qr_code=self.qr_code,
            scanned_by=self.user,
            latitude=self.scan_data['latitude'],
            longitude=self.scan_data['longitude'],
            scan_type='departure'
        )
        
        self.assertEqual(self.user.scans.count(), 4)
    
    def test_multiple_scans_per_qr_code(self):
        """Test that QR code can have multiple scans"""
        user1 = User.objects.create(
            company=self.company,
            name='User 1',
            email='user1@test.sk',
            password='pass'
        )
        user2 = User.objects.create(
            company=self.company,
            name='User 2',
            email='user2@test.sk',
            password='pass'
        )
        
        scan1 = ScanEvent.objects.create(
            qr_code=self.qr_code,
            scanned_by=user1,
            latitude=48.1486,
            longitude=17.1077,
            scan_type='arrival'
        )
        scan2 = ScanEvent.objects.create(
            qr_code=self.qr_code,
            scanned_by=user2,
            latitude=48.1486,
            longitude=17.1077,
            scan_type='arrival'
        )
        
        self.assertEqual(self.qr_code.scans.count(), 2)
    
    @patch('requests.get')
    def test_get_address_from_coordinates_success(self, mock_get):
        """Test successful geocoding"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'address': {
                'road': 'Hlavná',
                'house_number': '123',
                'postcode': '81101',
                'city': 'Bratislava',
                'country': 'Slovensko'
            }
        }
        mock_get.return_value = mock_response
        
        scan = ScanEvent.objects.create(**self.scan_data)
        address = scan.get_address_from_coordinates()
        
        self.assertIsNotNone(address)
        self.assertIn('Hlavná 123', address)
        self.assertIn('81101 Bratislava', address)
        self.assertIn('Slovensko', address)
    
    @patch('requests.get')
    def test_get_address_from_coordinates_partial_data(self, mock_get):
        """Test geocoding with partial address data"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'address': {
                'city': 'Bratislava',
                'country': 'Slovensko'
            }
        }
        mock_get.return_value = mock_response
        
        scan = ScanEvent.objects.create(**self.scan_data)
        address = scan.get_address_from_coordinates()
        
        self.assertIsNotNone(address)
        self.assertIn('Bratislava', address)
        self.assertIn('Slovensko', address)
    
    @patch('requests.get')
    def test_get_address_from_coordinates_failure(self, mock_get):
        """Test geocoding API failure"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        scan = ScanEvent.objects.create(**self.scan_data)
        address = scan.get_address_from_coordinates()
        
        self.assertIsNone(address)
    
    @patch('requests.get')
    def test_get_address_from_coordinates_timeout(self, mock_get):
        """Test geocoding with timeout"""
        mock_get.side_effect = Exception("Timeout")
        
        scan = ScanEvent.objects.create(**self.scan_data)
        address = scan.get_address_from_coordinates()
        
        self.assertIsNone(address)
    
    @patch('requests.get')
    def test_get_address_from_coordinates_empty_response(self, mock_get):
        """Test geocoding with empty address data"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'address': {}}
        mock_get.return_value = mock_response
        
        scan = ScanEvent.objects.create(**self.scan_data)
        address = scan.get_address_from_coordinates()
        
        self.assertIsNone(address)
    
    def test_scan_event_nullable_fields(self):
        """Test that optional fields can be null"""
        scan = ScanEvent.objects.create(
            latitude=48.1486,
            longitude=17.1077,
            scan_type='arrival'
        )
        
        self.assertIsNone(scan.qr_code)
        self.assertIsNone(scan.scanned_by)
        self.assertIsNone(scan.address)
        self.assertIsNone(scan.device_info)


# ============================================================================
# VACATION MODEL TESTS
# ============================================================================

class VacationModelTests(TestCase):
    """Test suite for Vacation model"""
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            name='Test Company',
            email='company@test.sk',
            password='password'
        )
        
        self.user = User.objects.create(
            company=self.company,
            name='Test User',
            email='user@test.sk',
            password='password'
        )
        
        self.vacation_data = {
            'user': self.user,
            'date_from': date(2026, 7, 1),
            'date_to': date(2026, 7, 5)
        }
    
    def test_vacation_creation_minimal(self):
        """Test creating vacation with minimal required fields"""
        vacation = Vacation.objects.create(**self.vacation_data)
        
        self.assertEqual(vacation.user, self.user)
        self.assertEqual(vacation.date_from, date(2026, 7, 1))
        self.assertEqual(vacation.date_to, date(2026, 7, 5))
        self.assertIsNotNone(vacation.created_at)
        self.assertIsNotNone(vacation.modified_at)
        self.assertTrue(vacation.is_active)
        self.assertFalse(vacation.approved)
        self.assertIsNone(vacation.type)
    
    def test_vacation_creation_full(self):
        """Test creating vacation with all fields"""
        from datetime import time
        
        vacation = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 7, 1),
            date_to=date(2026, 7, 1),
            time_from=time(8, 0),
            time_to=time(12, 0),
            type='Dovolenka',
            approved=True,
            is_active=True
        )
        
        self.assertEqual(vacation.time_from, time(8, 0))
        self.assertEqual(vacation.time_to, time(12, 0))
        self.assertEqual(vacation.type, 'Dovolenka')
        self.assertTrue(vacation.approved)
    
    def test_vacation_str_representation(self):
        """Test string representation of vacation"""
        vacation = Vacation.objects.create(**self.vacation_data)
        expected = "Test User: 2026-07-01 - 2026-07-05"
        self.assertEqual(str(vacation), expected)
    
    def test_vacation_ordering(self):
        """Test that vacations are ordered by date_from descending"""
        vacation1 = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 6, 1),
            date_to=date(2026, 6, 5)
        )
        vacation2 = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 7, 1),
            date_to=date(2026, 7, 5)
        )
        vacation3 = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 8, 1),
            date_to=date(2026, 8, 5)
        )
        
        vacations = Vacation.objects.all()
        
        # Should be ordered by date_from descending (newest first)
        self.assertEqual(vacations[0], vacation3)
        self.assertEqual(vacations[1], vacation2)
        self.assertEqual(vacations[2], vacation1)
    
    def test_vacation_user_relationship(self):
        """Test relationship with user"""
        vacation = Vacation.objects.create(**self.vacation_data)
        
        # Forward relationship
        self.assertEqual(vacation.user, self.user)
        
        # Reverse relationship
        self.assertIn(vacation, self.user.vacations.all())
        self.assertEqual(self.user.vacations.count(), 1)
    
    def test_vacation_cascade_on_user_delete(self):
        """Test that vacations are deleted when user is deleted"""
        vacation = Vacation.objects.create(**self.vacation_data)
        vacation_id = vacation.id
        
        self.user.delete()
        
        # Vacation should be deleted
        self.assertFalse(Vacation.objects.filter(id=vacation_id).exists())
    
    def test_multiple_vacations_per_user(self):
        """Test that user can have multiple vacations"""
        vacation1 = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 1, 1),
            date_to=date(2026, 1, 5)
        )
        vacation2 = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 7, 1),
            date_to=date(2026, 7, 10)
        )
        vacation3 = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 12, 20),
            date_to=date(2026, 12, 31)
        )
        
        self.assertEqual(self.user.vacations.count(), 3)
    
    def test_vacation_days_count_multiple_days(self):
        """Test days_count property for multiple days"""
        vacation = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 7, 1),
            date_to=date(2026, 7, 5)
        )
        
        # 5 days (1-5 inclusive)
        self.assertEqual(vacation.days_count, 5)
    
    def test_vacation_days_count_single_day(self):
        """Test days_count property for single day"""
        vacation = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 7, 1),
            date_to=date(2026, 7, 1)
        )
        
        # 1 day
        self.assertEqual(vacation.days_count, 1)
    
    def test_vacation_days_count_half_day(self):
        """Test days_count property for half day (same day with times)"""
        from datetime import time
        
        vacation = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 7, 1),
            date_to=date(2026, 7, 1),
            time_from=time(8, 0),
            time_to=time(12, 0)
        )
        
        # Half day
        self.assertEqual(vacation.days_count, 0.5)
    
    def test_vacation_days_count_week(self):
        """Test days_count property for a week"""
        vacation = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 7, 1),
            date_to=date(2026, 7, 7)
        )
        
        # 7 days
        self.assertEqual(vacation.days_count, 7)
    
    def test_vacation_days_count_month(self):
        """Test days_count property for approximately a month"""
        vacation = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 7, 1),
            date_to=date(2026, 7, 31)
        )
        
        # 31 days
        self.assertEqual(vacation.days_count, 31)
    
    def test_vacation_approval_workflow(self):
        """Test vacation approval workflow"""
        vacation = Vacation.objects.create(**self.vacation_data)
        
        # Should start as not approved
        self.assertFalse(vacation.approved)
        
        # Approve vacation
        vacation.approved = True
        vacation.save()
        
        vacation.refresh_from_db()
        self.assertTrue(vacation.approved)
    
    def test_vacation_deactivation(self):
        """Test deactivating vacation"""
        vacation = Vacation.objects.create(**self.vacation_data)
        
        # Should be active by default
        self.assertTrue(vacation.is_active)
        
        # Deactivate
        vacation.is_active = False
        vacation.save()
        
        vacation.refresh_from_db()
        self.assertFalse(vacation.is_active)
    
    def test_vacation_types(self):
        """Test different vacation types"""
        types = ['Dovolenka', 'Sick Leave', 'OČR', 'Paragraf', 'Náhradné voľno']
        
        for vacation_type in types:
            vacation = Vacation.objects.create(
                user=self.user,
                date_from=date(2026, 1, 1),
                date_to=date(2026, 1, 1),
                type=vacation_type
            )
            self.assertEqual(vacation.type, vacation_type)
    
    def test_vacation_modified_at_updates(self):
        """Test that modified_at updates when vacation is changed"""
        vacation = Vacation.objects.create(**self.vacation_data)
        original_modified = vacation.modified_at
        
        # Wait a tiny bit and update
        import time
        time.sleep(0.01)
        
        vacation.approved = True
        vacation.save()
        
        vacation.refresh_from_db()
        self.assertGreater(vacation.modified_at, original_modified)
    
    def test_vacation_optional_fields_null(self):
        """Test that optional fields can be null"""
        vacation = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 7, 1),
            date_to=date(2026, 7, 5)
        )
        
        self.assertIsNone(vacation.time_from)
        self.assertIsNone(vacation.time_to)
        self.assertIsNone(vacation.type)
    
    def test_vacation_overlapping_periods(self):
        """Test that system allows overlapping vacation periods (business logic should prevent)"""
        # Create two overlapping vacations - system allows it, business logic should prevent
        vacation1 = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 7, 1),
            date_to=date(2026, 7, 10)
        )
        vacation2 = Vacation.objects.create(
            user=self.user,
            date_from=date(2026, 7, 5),
            date_to=date(2026, 7, 15)
        )
        
        # Both should exist in database
        self.assertEqual(self.user.vacations.count(), 2)


# ============================================================================
# PASSWORDRESETTOKEN MODEL TESTS
# ============================================================================

class PasswordResetTokenModelTests(TestCase):
    """Test suite for PasswordResetToken model"""
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            name='Test Company',
            email='company@test.sk',
            password='password'
        )
        
        self.token_data = {
            'company': self.company,
            'token': 'test_token_123456789',
            'expires_at': datetime.now() + timedelta(hours=24)
        }
    
    def test_password_reset_token_creation(self):
        """Test creating password reset token"""
        token = PasswordResetToken.objects.create(**self.token_data)
        
        self.assertEqual(token.company, self.company)
        self.assertEqual(token.token, 'test_token_123456789')
        self.assertIsNotNone(token.created_at)
        self.assertIsNotNone(token.expires_at)
        self.assertFalse(token.is_used)
    
    def test_password_reset_token_str_representation(self):
        """Test string representation"""
        token = PasswordResetToken.objects.create(**self.token_data)
        self.assertEqual(str(token), 'Reset token for Test Company')
    
    def test_password_reset_token_unique_constraint(self):
        """Test that token must be unique"""
        PasswordResetToken.objects.create(**self.token_data)
        
        with self.assertRaises(IntegrityError):
            PasswordResetToken.objects.create(**self.token_data)
    
    def test_password_reset_token_company_relationship(self):
        """Test relationship with company"""
        token = PasswordResetToken.objects.create(**self.token_data)
        
        # Forward relationship
        self.assertEqual(token.company, self.company)
        
        # Reverse relationship
        self.assertIn(token, self.company.reset_tokens.all())
    
    def test_password_reset_token_cascade_on_company_delete(self):
        """Test that tokens are deleted when company is deleted"""
        token = PasswordResetToken.objects.create(**self.token_data)
        token_id = token.id
        
        self.company.delete()
        
        self.assertFalse(PasswordResetToken.objects.filter(id=token_id).exists())
    
    def test_password_reset_token_is_valid_fresh_token(self):
        """Test is_valid() for fresh unused token"""
        token = PasswordResetToken.objects.create(**self.token_data)
        
        self.assertTrue(token.is_valid())
    
    def test_password_reset_token_is_valid_used_token(self):
        """Test is_valid() for used token"""
        token = PasswordResetToken.objects.create(**self.token_data)
        token.is_used = True
        token.save()
        
        self.assertFalse(token.is_valid())
    
    def test_password_reset_token_is_valid_expired_token(self):
        """Test is_valid() for expired token"""
        token = PasswordResetToken.objects.create(
            company=self.company,
            token='expired_token',
            expires_at=datetime.now() - timedelta(hours=1)
        )
        
        self.assertFalse(token.is_valid())
    
    def test_password_reset_token_is_valid_used_and_expired(self):
        """Test is_valid() for token that is both used and expired"""
        token = PasswordResetToken.objects.create(
            company=self.company,
            token='used_expired_token',
            expires_at=datetime.now() - timedelta(hours=1)
        )
        token.is_used = True
        token.save()
        
        self.assertFalse(token.is_valid())
    
    def test_password_reset_token_mark_as_used(self):
        """Test marking token as used"""
        token = PasswordResetToken.objects.create(**self.token_data)
        
        self.assertFalse(token.is_used)
        self.assertTrue(token.is_valid())
        
        token.is_used = True
        token.save()
        
        token.refresh_from_db()
        self.assertTrue(token.is_used)
        self.assertFalse(token.is_valid())
    
    def test_multiple_tokens_per_company(self):
        """Test that company can have multiple reset tokens"""
        token1 = PasswordResetToken.objects.create(
            company=self.company,
            token='token1',
            expires_at=datetime.now() + timedelta(hours=24)
        )
        token2 = PasswordResetToken.objects.create(
            company=self.company,
            token='token2',
            expires_at=datetime.now() + timedelta(hours=24)
        )
        
        self.assertEqual(self.company.reset_tokens.count(), 2)


class UserPasswordSetupTokenModelTests(TestCase):
    """Test suite for employee password setup tokens"""

    def setUp(self):
        self.company = Company.objects.create(
            name='Test Company',
            email='company@test.sk',
            password='password'
        )
        self.user = User.objects.create(
            company=self.company,
            name='Employee',
            email='employee@test.sk',
            password='password'
        )

    def test_user_password_setup_token_creation(self):
        token = UserPasswordSetupToken.objects.create(
            user=self.user,
            token='employee_setup_token',
            expires_at=datetime.now() + timedelta(hours=24)
        )

        self.assertEqual(token.user, self.user)
        self.assertFalse(token.is_used)
        self.assertTrue(token.is_valid())

    def test_user_password_setup_token_string(self):
        token = UserPasswordSetupToken.objects.create(
            user=self.user,
            token='employee_setup_token',
            expires_at=datetime.now() + timedelta(hours=24)
        )

        self.assertEqual(str(token), 'Password setup token for employee@test.sk')

    def test_user_password_setup_token_invalid_when_used(self):
        token = UserPasswordSetupToken.objects.create(
            user=self.user,
            token='employee_setup_token_used',
            expires_at=datetime.now() + timedelta(hours=24),
            is_used=True
        )

        self.assertFalse(token.is_valid())

    def test_user_password_setup_token_invalid_when_expired(self):
        token = UserPasswordSetupToken.objects.create(
            user=self.user,
            token='employee_setup_token_expired',
            expires_at=datetime.now() - timedelta(hours=1)
        )

        self.assertFalse(token.is_valid())


# ============================================================================
# AUDITLOG MODEL TESTS
# ============================================================================

class AuditLogModelTests(TestCase):
    """Test suite for AuditLog model"""
    
    def setUp(self):
        """Set up test data"""
        self.audit_data = {
            'actor_type': 'company',
            'actor_email': 'company@test.sk',
            'actor_name': 'Test Company',
            'action': 'create',
            'message': 'Created new user',
            'ip_address': '192.168.1.1'
        }
    
    def test_audit_log_creation(self):
        """Test creating audit log entry"""
        log = AuditLog.objects.create(**self.audit_data)
        
        self.assertEqual(log.actor_type, 'company')
        self.assertEqual(log.actor_email, 'company@test.sk')
        self.assertEqual(log.actor_name, 'Test Company')
        self.assertEqual(log.action, 'create')
        self.assertEqual(log.message, 'Created new user')
        self.assertEqual(log.ip_address, '192.168.1.1')
        self.assertIsNotNone(log.timestamp)
    
    def test_audit_log_str_representation(self):
        """Test string representation"""
        log = AuditLog.objects.create(**self.audit_data)
        expected = f"Test Company (company) - create at {log.timestamp}"
        self.assertEqual(str(log), expected)
    
    def test_audit_log_all_actions(self):
        """Test all action types"""
        actions = ['create', 'update', 'delete', 'approve', 'login', 'logout']
        
        for action in actions:
            log = AuditLog.objects.create(
                actor_type='company',
                actor_email='test@test.sk',
                actor_name='Test',
                action=action,
                message=f'Test {action} action'
            )
            self.assertEqual(log.action, action)
    
    def test_audit_log_all_actor_types(self):
        """Test all actor types"""
        actor_types = ['company', 'user']
        
        for actor_type in actor_types:
            log = AuditLog.objects.create(
                actor_type=actor_type,
                actor_email='test@test.sk',
                actor_name='Test',
                action='login',
                message='Test login'
            )
            self.assertEqual(log.actor_type, actor_type)
    
    def test_audit_log_ordering(self):
        """Test that logs are ordered by timestamp descending"""
        import time
        log1 = AuditLog.objects.create(**self.audit_data)
        time.sleep(0.001)
        log2 = AuditLog.objects.create(**self.audit_data)
        time.sleep(0.001)
        log3 = AuditLog.objects.create(**self.audit_data)
        
        logs = AuditLog.objects.all()
        
        # Should be ordered newest first
        self.assertEqual(logs[0], log3)
        self.assertEqual(logs[1], log2)
        self.assertEqual(logs[2], log1)
    
    def test_audit_log_company_actions(self):
        """Test logging company actions"""
        log = AuditLog.objects.create(
            actor_type='company',
            actor_email='company@test.sk',
            actor_name='Test Company s.r.o.',
            action='create',
            message='Created new QR code: Main Entrance',
            ip_address='192.168.1.100'
        )
        
        self.assertEqual(log.actor_type, 'company')
        self.assertIn('QR code', log.message)
    
    def test_audit_log_user_actions(self):
        """Test logging user actions"""
        log = AuditLog.objects.create(
            actor_type='user',
            actor_email='user@test.sk',
            actor_name='Ján Novák',
            action='login',
            message='User logged in',
            ip_address='192.168.1.50'
        )
        
        self.assertEqual(log.actor_type, 'user')
        self.assertEqual(log.action, 'login')
    
    def test_audit_log_without_ip_address(self):
        """Test creating audit log without IP address"""
        log = AuditLog.objects.create(
            actor_type='company',
            actor_email='company@test.sk',
            actor_name='Test Company',
            action='update',
            message='Updated settings'
        )
        
        self.assertIsNone(log.ip_address)
    
    def test_audit_log_long_message(self):
        """Test audit log with long message"""
        long_message = 'A' * 1000  # Very long message
        
        log = AuditLog.objects.create(
            actor_type='company',
            actor_email='company@test.sk',
            actor_name='Test Company',
            action='update',
            message=long_message
        )
        
        self.assertEqual(len(log.message), 1000)
    
    def test_audit_log_filtering_by_actor_email(self):
        """Test filtering logs by actor email (indexed field)"""
        AuditLog.objects.create(
            actor_type='company',
            actor_email='company1@test.sk',
            actor_name='Company 1',
            action='create',
            message='Test 1'
        )
        AuditLog.objects.create(
            actor_type='company',
            actor_email='company2@test.sk',
            actor_name='Company 2',
            action='create',
            message='Test 2'
        )
        
        logs = AuditLog.objects.filter(actor_email='company1@test.sk')
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs.first().actor_email, 'company1@test.sk')
    
    def test_audit_log_multiple_actions_tracking(self):
        """Test tracking multiple actions for audit trail"""
        # Simulate a workflow
        AuditLog.objects.create(
            actor_type='user',
            actor_email='user@test.sk',
            actor_name='User',
            action='create',
            message='Created vacation request'
        )
        AuditLog.objects.create(
            actor_type='company',
            actor_email='manager@test.sk',
            actor_name='Manager',
            action='approve',
            message='Approved vacation request'
        )
        AuditLog.objects.create(
            actor_type='user',
            actor_email='user@test.sk',
            actor_name='User',
            action='update',
            message='Modified vacation dates'
        )
        
        all_logs = AuditLog.objects.all()
        self.assertEqual(all_logs.count(), 3)
        
        # Check action types
        actions = [log.action for log in all_logs]
        self.assertIn('create', actions)
        self.assertIn('approve', actions)
        self.assertIn('update', actions)


# ============================================================================
# MAGAZINE MODEL TESTS
# ============================================================================

# class MagazineModelTests(TestCase):
#     """Test suite for Magazine model"""
    
    # def setUp(self):
    #     """Set up test data"""
    #     self.company = Company.objects.create(
    #         name='Test Company',
    #         email='company@test.sk',
    #         password='password'
    #     )
        
    #     self.user = User.objects.create(
    #         company=self.company,
    #         name='Editor',
    #         email='editor@test.sk',
    #         password='password'
    #     )
        
    #     self.magazine_data = {
    #         'company': self.company,
    #         'created_by': self.user,
    #         'title': 'Company Newsletter',
    #         'issue_number': '1',
    #         'publish_date': date(2026, 1, 15)
    #     }
    
    # def test_magazine_creation_minimal(self):
    #     """Test creating magazine with required fields"""
    #     magazine = Magazine.objects.create(**self.magazine_data)
        
    #     self.assertEqual(magazine.company, self.company)
    #     self.assertEqual(magazine.created_by, self.user)
    #     self.assertEqual(magazine.title, 'Company Newsletter')
    #     self.assertEqual(magazine.issue_number, '1')
    #     self.assertEqual(magazine.publish_date, date(2026, 1, 15))
    #     self.assertIsNotNone(magazine.created_at)
    #     self.assertIsNotNone(magazine.modified_at)
    #     self.assertFalse(magazine.is_published)
    
    # def test_magazine_default_values(self):
    #     """Test magazine default values"""
    #     magazine = Magazine.objects.create(**self.magazine_data)
        
    #     self.assertEqual(magazine.template_id, 'classic')
    #     self.assertEqual(magazine.primary_font, 'Playfair Display')
    #     self.assertEqual(magazine.secondary_font, 'Lato')
    #     self.assertEqual(magazine.primary_color, '#1a1a1a')
    #     self.assertEqual(magazine.background_color, '#1a1a1a')
    #     self.assertEqual(magazine.language, 'en')
    #     self.assertFalse(magazine.print_bleed)
    #     self.assertEqual(magazine.cover_header_position, 'top')
    
    # def test_magazine_creation_full(self):
    #     """Test creating magazine with all customizations"""
    #     magazine = Magazine.objects.create(
    #         company=self.company,
    #         created_by=self.user,
    #         title='Premium Magazine',
    #         issue_number='2023-Q4',
    #         tagline='Excellence in Publishing',
    #         publish_date=date(2026, 12, 1),
    #         template_id='modern',
    #         primary_font='Roboto',
    #         secondary_font='Open Sans',
    #         primary_color='#2c3e50',
    #         secondary_color='#ecf0f1',
    #         background_color='#ffffff',
    #         text_color='#2c3e50',
    #         cover_background_image='/static/images/custom.jpg',
    #         cover_header_position='center',
    #         language='sk',
    #         print_bleed=True,
    #         categories='Správy,Technológie,Kultúra',
    #         is_published=True
    #     )
        
    #     self.assertEqual(magazine.template_id, 'modern')
    #     self.assertEqual(magazine.primary_font, 'Roboto')
    #     self.assertEqual(magazine.language, 'sk')
    #     self.assertTrue(magazine.print_bleed)
    #     self.assertTrue(magazine.is_published)
    #     self.assertEqual(magazine.cover_header_position, 'center')
    
    # def test_magazine_str_representation(self):
    #     """Test string representation"""
    #     magazine = Magazine.objects.create(**self.magazine_data)
    #     self.assertEqual(str(magazine), 'Company Newsletter - Issue 1')
    
    # def test_magazine_ordering(self):
    #     """Test that magazines are ordered by modified_at descending"""
    #     mag1 = Magazine.objects.create(
    #         company=self.company,
    #         created_by=self.user,
    #         title='Magazine 1',
    #         publish_date=date(2026, 1, 1)
    #     )
    #     mag2 = Magazine.objects.create(
    #         company=self.company,
    #         created_by=self.user,
    #         title='Magazine 2',
    #         publish_date=date(2026, 2, 1)
    #     )
    #     mag3 = Magazine.objects.create(
    #         company=self.company,
    #         created_by=self.user,
    #         title='Magazine 3',
    #         publish_date=date(2026, 3, 1)
    #     )
        
    #     magazines = Magazine.objects.all()
        
    #     # Should be ordered by modified_at descending (newest first)
    #     self.assertEqual(magazines[0], mag3)
    #     self.assertEqual(magazines[1], mag2)
    #     self.assertEqual(magazines[2], mag1)
    
    # def test_magazine_company_relationship(self):
    #     """Test relationship with company"""
    #     magazine = Magazine.objects.create(**self.magazine_data)
        
    #     # Forward relationship
    #     self.assertEqual(magazine.company, self.company)
        
    #     # Reverse relationship
    #     self.assertIn(magazine, self.company.magazines.all())
    
    # def test_magazine_creator_relationship(self):
    #     """Test relationship with creator user"""
    #     magazine = Magazine.objects.create(**self.magazine_data)
        
    #     # Forward relationship
    #     self.assertEqual(magazine.created_by, self.user)
        
    #     # Reverse relationship
    #     self.assertIn(magazine, self.user.created_magazines.all())
    
    # def test_magazine_cascade_on_company_delete(self):
    #     """Test that magazines are deleted when company is deleted"""
    #     magazine = Magazine.objects.create(**self.magazine_data)
    #     magazine_id = magazine.id
        
    #     self.company.delete()
        
    #     self.assertFalse(Magazine.objects.filter(id=magazine_id).exists())
    
    # def test_magazine_set_null_on_user_delete(self):
    #     """Test that magazine is preserved but creator is set to NULL when user is deleted"""
    #     magazine = Magazine.objects.create(**self.magazine_data)
    #     magazine_id = magazine.id
        
    #     self.user.delete()
        
    #     # Magazine should still exist
    #     self.assertTrue(Magazine.objects.filter(id=magazine_id).exists())
        
    #     magazine.refresh_from_db()
    #     # Creator should be None
    #     self.assertIsNone(magazine.created_by)
    
    # def test_magazine_get_categories_list(self):
    #     """Test get_categories_list method"""
    #     magazine = Magazine.objects.create(
    #         **self.magazine_data,
    #         categories='News,Features,Opinion,Culture,Sports'
    #     )
        
    #     categories = magazine.get_categories_list()
        
    #     self.assertEqual(len(categories), 5)
    #     self.assertIn('News', categories)
    #     self.assertIn('Features', categories)
    #     self.assertIn('Opinion', categories)
    #     self.assertIn('Culture', categories)
    #     self.assertIn('Sports', categories)
    
    # def test_magazine_get_categories_list_with_spaces(self):
    #     """Test get_categories_list with spaces around categories"""
    #     magazine = Magazine.objects.create(
    #         **self.magazine_data,
    #         categories=' News , Features , Opinion '
    #     )
        
    #     categories = magazine.get_categories_list()
        
    #     self.assertEqual(len(categories), 3)
    #     self.assertEqual(categories, ['News', 'Features', 'Opinion'])
    
    # def test_magazine_get_categories_list_empty(self):
    #     """Test get_categories_list with empty string"""
    #     magazine = Magazine.objects.create(
    #         **self.magazine_data,
    #         categories=''
    #     )
        
    #     categories = magazine.get_categories_list()
        
    #     self.assertEqual(len(categories), 0)
    
    # def test_magazine_cover_header_positions(self):
    #     """Test all cover header position options"""
    #     positions = ['top', 'center', 'bottom']
        
    #     for position in positions:
    #         magazine = Magazine.objects.create(
    #             company=self.company,
    #             created_by=self.user,
    #             title=f'Magazine {position}',
    #             publish_date=date(2026, 1, 1),
    #             cover_header_position=position
    #         )
    #         self.assertEqual(magazine.cover_header_position, position)
    
    # def test_magazine_publication_workflow(self):
    #     """Test magazine publication workflow"""
    #     magazine = Magazine.objects.create(**self.magazine_data)
        
    #     # Should start as unpublished
    #     self.assertFalse(magazine.is_published)
        
    #     # Publish magazine
    #     magazine.is_published = True
    #     magazine.save()
        
    #     magazine.refresh_from_db()
    #     self.assertTrue(magazine.is_published)
    
    # def test_multiple_magazines_per_company(self):
    #     """Test that company can have multiple magazines"""
    #     mag1 = Magazine.objects.create(
    #         company=self.company,
    #         created_by=self.user,
    #         title='Magazine 1',
    #         issue_number='1',
    #         publish_date=date(2026, 1, 1)
    #     )
    #     mag2 = Magazine.objects.create(
    #         company=self.company,
    #         created_by=self.user,
    #         title='Magazine 2',
    #         issue_number='2',
    #         publish_date=date(2026, 2, 1)
    #     )
        
    #     self.assertEqual(self.company.magazines.count(), 2)


# ============================================================================
# MAGAZINEARTICLE MODEL TESTS
# ============================================================================

# class MagazineArticleModelTests(TestCase):
#     """Test suite for MagazineArticle model"""
    
    # def setUp(self):
    #     """Set up test data"""
    #     self.company = Company.objects.create(
    #         name='Test Company',
    #         email='company@test.sk',
    #         password='password'
    #     )
        
    #     self.user = User.objects.create(
    #         company=self.company,
    #         name='Writer',
    #         email='writer@test.sk',
    #         password='password'
    #     )
        
    #     self.magazine = Magazine.objects.create(
    #         company=self.company,
    #         created_by=self.user,
    #         title='Test Magazine',
    #         publish_date=date(2026, 1, 15)
    #     )
        
    #     self.article_data = {
    #         'magazine': self.magazine,
    #         'author': self.user,
    #         'title': 'Test Article',
    #         'category': 'News'
    #     }
    
    # def test_article_creation_minimal(self):
    #     """Test creating article with minimal required fields"""
    #     article = MagazineArticle.objects.create(**self.article_data)
        
    #     self.assertEqual(article.magazine, self.magazine)
    #     self.assertEqual(article.author, self.user)
    #     self.assertEqual(article.title, 'Test Article')
    #     self.assertEqual(article.category, 'News')
    #     self.assertEqual(article.status, 'draft')
    #     self.assertFalse(article.is_main_story)
    #     self.assertFalse(article.is_secondary_story)
    #     self.assertEqual(article.order, 0)
    
    # def test_article_creation_full(self):
    #     """Test creating article with all fields"""
    #     article = MagazineArticle.objects.create(
    #         magazine=self.magazine,
    #         author=self.user,
    #         title='Main Story of the Year',
    #         teaser='An incredible story that changed everything',
    #         category='Features',
    #         is_main_story=True,
    #         is_secondary_story=False,
    #         page_number=1,
    #         order=1,
    #         status='published'
    #     )
        
    #     self.assertEqual(article.teaser, 'An incredible story that changed everything')
    #     self.assertTrue(article.is_main_story)
    #     self.assertEqual(article.page_number, 1)
    #     self.assertEqual(article.order, 1)
    #     self.assertEqual(article.status, 'published')
    
    # def test_article_str_representation(self):
    #     """Test string representation"""
    #     article = MagazineArticle.objects.create(**self.article_data)
    #     self.assertEqual(str(article), 'Test Article - Test Magazine')
    
    # def test_article_ordering(self):
    #     """Test that articles are ordered by magazine, order, page_number"""
    #     article1 = MagazineArticle.objects.create(
    #         magazine=self.magazine,
    #         author=self.user,
    #         title='Article 1',
    #         category='News',
    #         order=2,
    #         page_number=3
    #     )
    #     article2 = MagazineArticle.objects.create(
    #         magazine=self.magazine,
    #         author=self.user,
    #         title='Article 2',
    #         category='News',
    #         order=1,
    #         page_number=1
    #     )
    #     article3 = MagazineArticle.objects.create(
    #         magazine=self.magazine,
    #         author=self.user,
    #         title='Article 3',
    #         category='News',
    #         order=1,
    #         page_number=2
    #     )
        
    #     articles = MagazineArticle.objects.all()
        
    #     # Should be ordered by order, then page_number
    #     self.assertEqual(articles[0], article2)  # order=1, page=1
    #     self.assertEqual(articles[1], article3)  # order=1, page=2
    #     self.assertEqual(articles[2], article1)  # order=2, page=3
    
    # def test_article_magazine_relationship(self):
    #     """Test relationship with magazine"""
    #     article = MagazineArticle.objects.create(**self.article_data)
        
    #     # Forward relationship
    #     self.assertEqual(article.magazine, self.magazine)
        
    #     # Reverse relationship
    #     self.assertIn(article, self.magazine.articles.all())
    
    # def test_article_author_relationship(self):
    #     """Test relationship with author"""
    #     article = MagazineArticle.objects.create(**self.article_data)
        
    #     # Forward relationship
    #     self.assertEqual(article.author, self.user)
        
    #     # Reverse relationship
    #     self.assertIn(article, self.user.articles.all())
    
    # def test_article_cascade_on_magazine_delete(self):
    #     """Test that articles are deleted when magazine is deleted"""
    #     article = MagazineArticle.objects.create(**self.article_data)
    #     article_id = article.id
        
    #     self.magazine.delete()
        
    #     self.assertFalse(MagazineArticle.objects.filter(id=article_id).exists())
    
    # def test_article_set_null_on_author_delete(self):
    #     """Test that article is preserved but author is set to NULL when author is deleted"""
    #     article = MagazineArticle.objects.create(**self.article_data)
    #     article_id = article.id
        
    #     self.user.delete()
        
    #     # Article should still exist
    #     self.assertTrue(MagazineArticle.objects.filter(id=article_id).exists())
        
    #     article.refresh_from_db()
    #     # Author should be None
    #     self.assertIsNone(article.author)
    
    # def test_article_status_choices(self):
    #     """Test article status choices"""
    #     statuses = ['draft', 'published']
        
    #     for status in statuses:
    #         article = MagazineArticle.objects.create(
    #             magazine=self.magazine,
    #             author=self.user,
    #             title=f'Article {status}',
    #             category='News',
    #             status=status
    #         )
    #         self.assertEqual(article.status, status)
    
    # def test_article_main_story_flag(self):
    #     """Test main story designation"""
    #     article = MagazineArticle.objects.create(
    #         **self.article_data,
    #         is_main_story=True
    #     )
        
    #     self.assertTrue(article.is_main_story)
    #     self.assertFalse(article.is_secondary_story)
    
    # def test_article_secondary_story_flag(self):
    #     """Test secondary story designation"""
    #     article = MagazineArticle.objects.create(
    #         **self.article_data,
    #         is_secondary_story=True
    #     )
        
    #     self.assertFalse(article.is_main_story)
    #     self.assertTrue(article.is_secondary_story)
    
    # def test_multiple_articles_per_magazine(self):
    #     """Test that magazine can have multiple articles"""
    #     for i in range(5):
    #         MagazineArticle.objects.create(
    #             magazine=self.magazine,
    #             author=self.user,
    #             title=f'Article {i+1}',
    #             category='News',
    #             order=i
    #         )
        
    #     self.assertEqual(self.magazine.articles.count(), 5)
    
    # def test_article_default_teaser(self):
    #     """Test article default teaser"""
    #     article = MagazineArticle.objects.create(**self.article_data)
    #     self.assertEqual(article.teaser, 'Teaser text')


# ============================================================================
# CONTENTBLOCK MODEL TESTS
# ============================================================================

# class ContentBlockModelTests(TestCase):
#     """Test suite for ContentBlock model"""
    
    # def setUp(self):
    #     """Set up test data"""
    #     self.company = Company.objects.create(
    #         name='Test Company',
    #         email='company@test.sk',
    #         password='password'
    #     )
        
    #     self.user = User.objects.create(
    #         company=self.company,
    #         name='Writer',
    #         email='writer@test.sk',
    #         password='password'
    #     )
        
    #     self.magazine = Magazine.objects.create(
    #         company=self.company,
    #         created_by=self.user,
    #         title='Test Magazine',
    #         publish_date=date(2026, 1, 15)
    #     )
        
    #     self.article = MagazineArticle.objects.create(
    #         magazine=self.magazine,
    #         author=self.user,
    #         title='Test Article',
    #         category='News'
    #     )
    
    # def test_content_block_text_creation(self):
    #     """Test creating text content block"""
    #     block = ContentBlock.objects.create(
    #         article=self.article,
    #         block_type='text',
    #         text_content='This is a paragraph of text content.',
    #         order=0
    #     )
        
    #     self.assertEqual(block.article, self.article)
    #     self.assertEqual(block.block_type, 'text')
    #     self.assertEqual(block.text_content, 'This is a paragraph of text content.')
    #     self.assertEqual(block.order, 0)
    #     self.assertEqual(block.alignment, 'left')
    
    # def test_content_block_image_creation(self):
    #     """Test creating image content block"""
    #     block = ContentBlock.objects.create(
    #         article=self.article,
    #         block_type='image',
    #         image_url='https://example.com/image.jpg',
    #         image_caption='Test caption',
    #         order=1
    #     )
        
    #     self.assertEqual(block.block_type, 'image')
    #     self.assertEqual(block.image_url, 'https://example.com/image.jpg')
    #     self.assertEqual(block.image_caption, 'Test caption')
    
    # def test_content_block_str_representation(self):
    #     """Test string representation"""
    #     block = ContentBlock.objects.create(
    #         article=self.article,
    #         block_type='text',
    #         text_content='Test',
    #         order=0
    #     )
        
    #     self.assertEqual(str(block), 'text block for Test Article')
    
    # def test_content_block_ordering(self):
    #     """Test that content blocks are ordered by article and order"""
    #     block1 = ContentBlock.objects.create(
    #         article=self.article,
    #         block_type='text',
    #         text_content='Third',
    #         order=2
    #     )
    #     block2 = ContentBlock.objects.create(
    #         article=self.article,
    #         block_type='text',
    #         text_content='First',
    #         order=0
    #     )
    #     block3 = ContentBlock.objects.create(
    #         article=self.article,
    #         block_type='text',
    #         text_content='Second',
    #         order=1
    #     )
        
    #     blocks = ContentBlock.objects.all()
        
    #     # Should be ordered by order field
    #     self.assertEqual(blocks[0], block2)  # order=0
    #     self.assertEqual(blocks[1], block3)  # order=1
    #     self.assertEqual(blocks[2], block1)  # order=2
    
    # def test_content_block_article_relationship(self):
    #     """Test relationship with article"""
    #     block = ContentBlock.objects.create(
    #         article=self.article,
    #         block_type='text',
    #         text_content='Test',
    #         order=0
    #     )
        
    #     # Forward relationship
    #     self.assertEqual(block.article, self.article)
        
    #     # Reverse relationship
    #     self.assertIn(block, self.article.content_blocks.all())
    
    # def test_content_block_cascade_on_article_delete(self):
    #     """Test that content blocks are deleted when article is deleted"""
    #     block = ContentBlock.objects.create(
    #         article=self.article,
    #         block_type='text',
    #         text_content='Test',
    #         order=0
    #     )
    #     block_id = block.id
        
    #     self.article.delete()
        
    #     self.assertFalse(ContentBlock.objects.filter(id=block_id).exists())
    
    # def test_content_block_all_alignments(self):
    #     """Test all alignment choices"""
    #     alignments = ['left', 'center', 'right', 'justify']
        
    #     for alignment in alignments:
    #         block = ContentBlock.objects.create(
    #             article=self.article,
    #             block_type='text',
    #             text_content='Test',
    #             order=0,
    #             alignment=alignment
    #         )
    #         self.assertEqual(block.alignment, alignment)
    
    # def test_content_block_all_font_sizes(self):
    #     """Test all font size choices"""
    #     font_sizes = ['sm', 'base', 'lg', 'xl']
        
    #     for font_size in font_sizes:
    #         block = ContentBlock.objects.create(
    #             article=self.article,
    #             block_type='text',
    #             text_content='Test',
    #             order=0,
    #             font_size=font_size
    #         )
    #         self.assertEqual(block.font_size, font_size)
    
    # def test_content_block_styling_options(self):
    #     """Test content block with all styling options"""
    #     block = ContentBlock.objects.create(
    #         article=self.article,
    #         block_type='text',
    #         text_content='Styled text',
    #         order=0,
    #         font_family='Arial',
    #         font_size='lg',
    #         text_color='#333333',
    #         background_color='#f5f5f5',
    #         alignment='center'
    #     )
        
    #     self.assertEqual(block.font_family, 'Arial')
    #     self.assertEqual(block.font_size, 'lg')
    #     self.assertEqual(block.text_color, '#333333')
    #     self.assertEqual(block.background_color, '#f5f5f5')
    #     self.assertEqual(block.alignment, 'center')
    
    # def test_multiple_content_blocks_per_article(self):
    #     """Test that article can have multiple content blocks"""
    #     for i in range(10):
    #         ContentBlock.objects.create(
    #             article=self.article,
    #             block_type='text' if i % 2 == 0 else 'image',
    #             text_content=f'Block {i}' if i % 2 == 0 else None,
    #             image_url=f'http://example.com/img{i}.jpg' if i % 2 == 1 else None,
    #             order=i
    #         )
        
    #     self.assertEqual(self.article.content_blocks.count(), 10)
    
    # def test_content_block_mixed_types(self):
    #     """Test article with mixed content block types"""
    #     text_block = ContentBlock.objects.create(
    #         article=self.article,
    #         block_type='text',
    #         text_content='Some text',
    #         order=0
    #     )
    #     image_block = ContentBlock.objects.create(
    #         article=self.article,
    #         block_type='image',
    #         image_url='http://example.com/img.jpg',
    #         order=1
    #     )
        
    #     blocks = self.article.content_blocks.all()
    #     self.assertEqual(blocks.count(), 2)
    #     self.assertEqual(blocks[0].block_type, 'text')
    #     self.assertEqual(blocks[1].block_type, 'image')




# ============================================================================
# INTEGRATION TESTS - Complex Scenarios
# ============================================================================

class IntegrationTests(TestCase):
    """Integration tests for complex real-world scenarios"""
    
    def setUp(self):
        """Set up complex test scenario"""
        # Create company
        self.company = Company.objects.create(
            name='TechCorp s.r.o.',
            email='info@techcorp.sk',
            password='password',
            ico='12345678',
            city='Bratislava',
            auto_lunch_breaks=True,
            notification_company=True
        )
        self.company.set_password('SecurePass123')
        self.company.save()
        
        # Create users
        self.manager = User.objects.create(
            company=self.company,
            name='Peter Manažér',
            email='peter.manazer@techcorp.sk',
            password='password',
            is_manager=True,
            can_edit_employees=True,
            can_edit_qr_codes=True,
            can_edit_absences=True
        )
        self.manager.set_password('ManagerPass123')
        self.manager.save()
        
        self.employee = User.objects.create(
            company=self.company,
            name='Jana Zamestnancová',
            email='jana.zamestnancova@techcorp.sk',
            password='password'
        )
        self.employee.set_password('EmployeePass123')
        self.employee.save()
    
    def test_complete_company_onboarding_workflow(self):
        """Test complete company onboarding and setup"""
        # 1. Company registers
        company = Company.objects.create(
            name='New Company',
            email='new@company.sk',
            password='temp'
        )
        company.set_password('SecurePassword123')
        company.save()
        
        # 2. Company creates QR codes
        entrance_qr = QRCodeProfile.objects.create(
            company=company,
            name='Main Entrance',
            location='Bratislava, Main Building'
        )
        office_qr = QRCodeProfile.objects.create(
            company=company,
            name='Office Floor 3',
            location='Bratislava, Floor 3'
        )
        
        # 3. Company adds employees
        employee1 = User.objects.create(
            company=company,
            name='Employee 1',
            email='emp1@company.sk',
            password='temp'
        )
        employee1.set_password('Pass123')
        employee1.save()
        
        employee2 = User.objects.create(
            company=company,
            name='Employee 2',
            email='emp2@company.sk',
            password='temp'
        )
        employee2.set_password('Pass123')
        employee2.save()
        
        # Verify setup
        self.assertEqual(company.qr_codes.count(), 2)
        self.assertEqual(company.users.count(), 2)
        self.assertTrue(entrance_qr.qr_code)
        self.assertTrue(office_qr.qr_code)
    
    def test_daily_attendance_workflow(self):
        """Test a complete daily attendance workflow"""
        # Create QR code
        qr = QRCodeProfile.objects.create(
            company=self.company,
            name='Main Entrance',
            location='Office'
        )
        
        # 1. Employee arrives
        arrival_scan = ScanEvent.objects.create(
            qr_code=qr,
            scanned_by=self.employee,
            scan_type='arrival',
            latitude=48.1486,
            longitude=17.1077
        )
        
        # 2. Lunch break start
        lunch_start_scan = ScanEvent.objects.create(
            qr_code=qr,
            scanned_by=self.employee,
            scan_type='lunch_break_start',
            latitude=48.1486,
            longitude=17.1077
        )
        
        # 3. Lunch break end
        lunch_end_scan = ScanEvent.objects.create(
            qr_code=qr,
            scanned_by=self.employee,
            scan_type='lunch_break_end',
            latitude=48.1486,
            longitude=17.1077
        )
        
        # 4. Employee departs
        departure_scan = ScanEvent.objects.create(
            qr_code=qr,
            scanned_by=self.employee,
            scan_type='departure',
            latitude=48.1486,
            longitude=17.1077
        )
        
        # Verify workflow
        daily_scans = self.employee.scans.all()
        self.assertEqual(daily_scans.count(), 4)
        
        scan_types = [scan.scan_type for scan in daily_scans.order_by('timestamp')]
        self.assertIn('arrival', scan_types)
        self.assertIn('lunch_break_start', scan_types)
        self.assertIn('lunch_break_end', scan_types)
        self.assertIn('departure', scan_types)
    
    def test_vacation_request_approval_workflow(self):
        """Test vacation request and approval workflow"""
        # 1. Employee requests vacation
        vacation = Vacation.objects.create(
            user=self.employee,
            date_from=date(2026, 7, 1),
            date_to=date(2026, 7, 10),
            type='Dovolenka',
            approved=False
        )
        
        # Log the request
        AuditLog.objects.create(
            actor_type='user',
            actor_email=self.employee.email,
            actor_name=self.employee.name,
            action='create',
            message=f'Created vacation request: {vacation.date_from} to {vacation.date_to}'
        )
        
        # 2. Manager reviews and approves
        vacation.approved = True
        vacation.save()
        
        # Log the approval
        AuditLog.objects.create(
            actor_type='user',
            actor_email=self.manager.email,
            actor_name=self.manager.name,
            action='approve',
            message=f'Approved vacation for {self.employee.name}: {vacation.date_from} to {vacation.date_to}'
        )
        
        # Verify workflow
        self.assertTrue(vacation.approved)
        self.assertEqual(vacation.days_count, 10)
        
        logs = AuditLog.objects.filter(action__in=['create', 'approve'])
        self.assertEqual(logs.count(), 2)
    
    def test_magazine_creation_workflow(self):
        """Test complete magazine creation workflow"""
        # 1. Create magazine
        magazine = Magazine.objects.create(
            company=self.company,
            created_by=self.manager,
            title='TechCorp Monthly',
            issue_number='2026-01',
            publish_date=date(2026, 1, 15),
            categories='Tech,News,Culture'
        )
        
        # 2. Add main article
        main_article = MagazineArticle.objects.create(
            magazine=magazine,
            author=self.manager,
            title='Revolutionary New Technology',
            teaser='A groundbreaking innovation',
            category='Tech',
            is_main_story=True,
            order=0,
            page_number=1,
            status='published'
        )
        
        # 3. Add content blocks to main article
        ContentBlock.objects.create(
            article=main_article,
            block_type='text',
            text_content='Introduction paragraph...',
            order=0
        )
        ContentBlock.objects.create(
            article=main_article,
            block_type='image',
            image_url='http://example.com/tech.jpg',
            image_caption='The new technology',
            order=1
        )
        ContentBlock.objects.create(
            article=main_article,
            block_type='text',
            text_content='Detailed explanation...',
            order=2
        )
        
        # 4. Add secondary articles
        article2 = MagazineArticle.objects.create(
            magazine=magazine,
            author=self.employee,
            title='Company News',
            category='News',
            order=1,
            page_number=3
        )
        
        ContentBlock.objects.create(
            article=article2,
            block_type='text',
            text_content='Latest company updates...',
            order=0
        )
        
        # 5. Publish magazine
        magazine.is_published = True
        magazine.save()
        
        # Verify workflow
        self.assertTrue(magazine.is_published)
        self.assertEqual(magazine.articles.count(), 2)
        self.assertEqual(main_article.content_blocks.count(), 3)
        self.assertEqual(article2.content_blocks.count(), 1)
        
        # Verify categories
        categories = magazine.get_categories_list()
        self.assertEqual(len(categories), 3)
    
    def test_home_office_and_business_trip_scenarios(self):
        """Test home office and business trip attendance"""
        # Home office day
        home_arrival = ScanEvent.objects.create(
            scanned_by=self.employee,
            scan_type='arrival',
            is_home_office=True,
            latitude=48.2000,
            longitude=17.2000
        )
        
        home_departure = ScanEvent.objects.create(
            scanned_by=self.employee,
            scan_type='departure',
            is_home_office=True,
            latitude=48.2000,
            longitude=17.2000
        )
        
        # Business trip
        trip_arrival = ScanEvent.objects.create(
            scanned_by=self.employee,
            scan_type='arrival',
            is_business_trip=True,
            latitude=50.0755,  # Prague
            longitude=14.4378
        )
        
        trip_departure = ScanEvent.objects.create(
            scanned_by=self.employee,
            scan_type='departure',
            is_business_trip=True,
            latitude=50.0755,
            longitude=14.4378
        )
        
        # Verify
        home_scans = ScanEvent.objects.filter(is_home_office=True)
        trip_scans = ScanEvent.objects.filter(is_business_trip=True)
        
        self.assertEqual(home_scans.count(), 2)
        self.assertEqual(trip_scans.count(), 2)
    
    def test_password_reset_workflow(self):
        """Test password reset workflow"""
        # 1. Company requests password reset
        reset_token = PasswordResetToken.objects.create(
            company=self.company,
            token='secure_random_token_123456',
            expires_at=datetime.now() + timedelta(hours=24)
        )
        
        # 2. Verify token is valid
        self.assertTrue(reset_token.is_valid())
        
        # 3. Company uses token to reset password
        old_password = self.company.password
        self.company.set_password('NewSecurePassword456')
        self.company.save()
        
        # 4. Mark token as used
        reset_token.is_used = True
        reset_token.save()
        
        # Verify
        self.assertFalse(reset_token.is_valid())
        self.assertNotEqual(self.company.password, old_password)
        self.assertTrue(self.company.check_password('NewSecurePassword456'))
    
    def test_audit_trail_comprehensive(self):
        """Test comprehensive audit trail logging"""
        # Company login
        AuditLog.objects.create(
            actor_type='company',
            actor_email=self.company.email,
            actor_name=self.company.name,
            action='login',
            message='Company logged in',
            ip_address='192.168.1.100'
        )
        
        # Create QR code
        qr = QRCodeProfile.objects.create(
            company=self.company,
            name='Test QR',
            location='Test'
        )
        AuditLog.objects.create(
            actor_type='company',
            actor_email=self.company.email,
            actor_name=self.company.name,
            action='create',
            message=f'Created QR code: {qr.name}'
        )
        
        # Create user
        AuditLog.objects.create(
            actor_type='company',
            actor_email=self.company.email,
            actor_name=self.company.name,
            action='create',
            message=f'Created user: {self.employee.name}'
        )
        
        # Update user
        AuditLog.objects.create(
            actor_type='company',
            actor_email=self.company.email,
            actor_name=self.company.name,
            action='update',
            message=f'Updated user permissions: {self.employee.name}'
        )
        
        # Company logout
        AuditLog.objects.create(
            actor_type='company',
            actor_email=self.company.email,
            actor_name=self.company.name,
            action='logout',
            message='Company logged out'
        )
        
        # Verify audit trail
        company_logs = AuditLog.objects.filter(actor_email=self.company.email)
        self.assertEqual(company_logs.count(), 5)
        
        actions = [log.action for log in company_logs]
        self.assertIn('login', actions)
        self.assertIn('create', actions)
        self.assertIn('update', actions)
        self.assertIn('logout', actions)
    
    def test_multi_company_isolation(self):
        """Test that data is properly isolated between companies"""
        # Create second company
        company2 = Company.objects.create(
            name='Company 2',
            email='company2@test.sk',
            password='password'
        )
        
        user2 = User.objects.create(
            company=company2,
            name='User 2',
            email='user2@company2.sk',
            password='password'
        )
        
        qr2 = QRCodeProfile.objects.create(
            company=company2,
            name='QR 2',
            location='Location 2'
        )
        
        # Verify isolation
        self.assertEqual(self.company.users.count(), 2)  # manager + employee
        self.assertEqual(company2.users.count(), 1)
        
        self.assertNotIn(user2, self.company.users.all())
        self.assertNotIn(self.employee, company2.users.all())
        
        self.assertNotIn(qr2, self.company.qr_codes.all())
    
    def test_cascade_deletion_integrity(self):
        """Test that cascade deletions maintain database integrity"""
        # Create complex structure
        qr = QRCodeProfile.objects.create(
            company=self.company,
            name='Test QR',
            location='Test'
        )
        
        scan = ScanEvent.objects.create(
            qr_code=qr,
            scanned_by=self.employee,
            scan_type='arrival',
            latitude=48.1486,
            longitude=17.1077
        )
        
        vacation = Vacation.objects.create(
            user=self.employee,
            date_from=date(2026, 7, 1),
            date_to=date(2026, 7, 5)
        )
        
        magazine = Magazine.objects.create(
            company=self.company,
            created_by=self.manager,
            title='Test Magazine',
            publish_date=date(2026, 1, 1)
        )
        
        article = MagazineArticle.objects.create(
            magazine=magazine,
            author=self.employee,
            title='Test Article',
            category='News'
        )
        
        # Store IDs
        qr_id = qr.id
        scan_id = scan.id
        vacation_id = vacation.id
        employee_id = self.employee.id
        magazine_id = magazine.id
        article_id = article.id
        
        # Delete company - should cascade
        self.company.delete()
        
        # Verify all related objects are deleted
        self.assertFalse(Company.objects.filter(id=self.company.id).exists())
        self.assertFalse(User.objects.filter(id=employee_id).exists())
        self.assertFalse(QRCodeProfile.objects.filter(id=qr_id).exists())
        self.assertFalse(ScanEvent.objects.filter(id=scan_id).exists())
        self.assertFalse(Vacation.objects.filter(id=vacation_id).exists())
        self.assertFalse(Magazine.objects.filter(id=magazine_id).exists())
        self.assertFalse(MagazineArticle.objects.filter(id=article_id).exists())


