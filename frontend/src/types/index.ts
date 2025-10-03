export interface User {
  id: string;
  email: string;
  role: 'admin' | 'operator' | 'manager';
  name: string;
}

export interface Product {
  id: string;
  name: string;
  category: string;
}

export interface Vendor {
  id: string;
  name: string;
  productIds: string[];
}

export interface ComplianceReport {
  id: string;
  fileName: string;
  productId: string;
  vendorId: string;
  uploadDate: string;
  status: 'compliant' | 'non-compliant' | 'pending' | 'error';
  uploadedBy: string;
  fileSize: number;
  complianceFlags: ComplianceFlag[];
}

export interface ComplianceFlag {
  id: string;
  type: 'error' | 'warning' | 'info';
  message: string;
  section: string;
  isResolved: boolean;
}

export interface Alert {
  id: string;
  reportId: string;
  message: string;
  severity: 'high' | 'medium' | 'low';
  status: 'pending' | 'acknowledged';
  createdAt: string;
}

export interface AuditLog {
  id: string;
  userId: string;
  userName: string;
  action: string;
  details: string;
  timestamp: string;
  reportId?: string;
}

export interface DashboardStats {
  totalUploads: number;
  compliantReports: number;
  nonCompliantReports: number;
  pendingReports: number;
  recentAlerts: number;
}