import os
from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://de_de:PUPB8V0s2b3bvNZUblolz7d6UM9bcBzb@dpg-d1h53rffte5s739b1i40-a.oregon-postgres.render.com/dwg_analyzer_pro')
Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(50), default='active')
    project_type = Column(String(100))
    building_type = Column(String(100))
    total_area = Column(Float)
    floor_count = Column(Integer, default=1)
    settings = Column(JSON)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="project")
    dwg_files = relationship("DWGFile", back_populates="project")
    collaborators = relationship("ProjectCollaborator", back_populates="project")

class DWGFile(Base):
    __tablename__ = 'dwg_files'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    floor_number = Column(Integer)
    zones_count = Column(Integer)
    layers = Column(JSON)
    bounds = Column(JSON)
    
    # Relationships
    project = relationship("Project", back_populates="dwg_files")
    zones = relationship("Zone", back_populates="dwg_file")

class Zone(Base):
    __tablename__ = 'zones'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dwg_file_id = Column(UUID(as_uuid=True), ForeignKey('dwg_files.id'))
    zone_name = Column(String(100))
    layer_name = Column(String(100))
    area = Column(Float)
    perimeter = Column(Float)
    points = Column(JSON)  # Store polygon coordinates
    bounds = Column(JSON)  # Bounding box
    room_type = Column(String(100))
    confidence_score = Column(Float)
    
    # Relationships
    dwg_file = relationship("DWGFile", back_populates="zones")
    placements = relationship("FurniturePlacement", back_populates="zone")

class Analysis(Base):
    __tablename__ = 'analyses'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    analysis_type = Column(String(50))  # 'standard', 'advanced', 'bim', 'multi_floor'
    parameters = Column(JSON)
    results = Column(JSON)
    total_boxes = Column(Integer)
    efficiency_score = Column(Float)
    space_utilization = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='completed')
    
    # Relationships
    project = relationship("Project", back_populates="analyses")

class FurniturePlacement(Base):
    __tablename__ = 'furniture_placements'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(UUID(as_uuid=True), ForeignKey('zones.id'))
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id'))
    position_x = Column(Float)
    position_y = Column(Float)
    width = Column(Float)
    height = Column(Float)
    rotation = Column(Float, default=0.0)
    suitability_score = Column(Float)
    furniture_type = Column(String(100))
    
    # Relationships
    zone = relationship("Zone", back_populates="placements")

class BIMModel(Base):
    __tablename__ = 'bim_models'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    model_data = Column(JSON)
    ifc_compliance_score = Column(Float)
    cobie_data = Column(JSON)
    standards_compliance = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class FurnitureConfiguration(Base):
    __tablename__ = 'furniture_configurations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    space_type = Column(String(100))
    total_items = Column(Integer)
    total_cost = Column(Float)
    sustainability_score = Column(Float)
    ergonomic_score = Column(Float)
    configuration_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProjectCollaborator(Base):
    __tablename__ = 'project_collaborators'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    user_id = Column(String(255))
    username = Column(String(255))
    role = Column(String(50))  # 'admin', 'architect', 'designer', 'viewer'
    permissions = Column(JSON)
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime)
    status = Column(String(50), default='active')
    
    # Relationships
    project = relationship("Project", back_populates="collaborators")

class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    user_id = Column(String(255))
    username = Column(String(255))
    content = Column(Text)
    x_position = Column(Float)
    y_position = Column(Float)
    zone_id = Column(UUID(as_uuid=True), ForeignKey('zones.id'), nullable=True)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ExportHistory(Base):
    __tablename__ = 'export_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    export_type = Column(String(50))  # 'pdf', 'dxf', 'ifc', 'json', 'csv'
    file_name = Column(String(255))
    file_size = Column(Integer)
    export_settings = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(255))

class DatabaseManager:
    """
    Comprehensive database manager for the AI Architectural Space Analyzer
    """
    
    def __init__(self, database_url=None):
        # Use provided URL or environment variable or default PostgreSQL
        DATABASE_URL = database_url or os.environ.get('DATABASE_URL') or 'postgresql://de_de:PUPB8V0s2b3bvNZUblolz7d6UM9bcBzb@dpg-d1h53rffte5s739b1i40-a.oregon-postgres.render.com/dwg_analyzer_pro'
        
        try:
            # Try PostgreSQL connection first
            self.engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute('SELECT 1')
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            print("✅ PostgreSQL database connected successfully")
        except Exception as e:
            print(f"PostgreSQL connection failed: {str(e)}")
            try:
                # Fallback to SQLite
                DATABASE_URL = "sqlite:///dwg_analyzer.db"
                self.engine = create_engine(DATABASE_URL)
                Base.metadata.create_all(self.engine)
                self.Session = sessionmaker(bind=self.engine)
                print("⚠️ Using SQLite database as fallback")
            except Exception as fallback_error:
                print(f"SQLite fallback failed: {str(fallback_error)}")
                # Last resort: in-memory SQLite
                DATABASE_URL = "sqlite:///:memory:"
                self.engine = create_engine(DATABASE_URL)
                Base.metadata.create_all(self.engine)
                self.Session = sessionmaker(bind=self.engine)
                print("⚠️ Using in-memory database as last resort")
    
    def get_session(self):
        """Get database session"""
        return self.Session()
    
    def create_project(self, name: str, description: str, created_by: str, 
                      project_type: str = 'single_floor', **kwargs) -> str:
        """Create new project"""
        session = self.get_session()
        try:
            project = Project(
                name=name,
                description=description,
                created_by=created_by,
                project_type=project_type,
                building_type=kwargs.get('building_type'),
                floor_count=kwargs.get('floor_count', 1),
                settings=kwargs.get('settings', {})
            )
            session.add(project)
            session.commit()
            project_id = str(project.id)
            return project_id
        finally:
            session.close()
    
    def save_dwg_file(self, project_id: str, filename: str, zones_data: List[Dict], 
                     **kwargs) -> str:
        """Save DWG file and zones data"""
        session = self.get_session()
        try:
            # Create DWG file record
            dwg_file = DWGFile(
                project_id=project_id,
                filename=filename,
                original_filename=kwargs.get('original_filename', filename),
                file_size=kwargs.get('file_size', 0),
                floor_number=kwargs.get('floor_number', 1),
                zones_count=len(zones_data),
                layers=kwargs.get('layers', []),
                bounds=kwargs.get('bounds')
            )
            session.add(dwg_file)
            session.flush()
            
            # Save zones
            for i, zone_data in enumerate(zones_data):
                zone = Zone(
                    dwg_file_id=dwg_file.id,
                    zone_name=f"Zone_{i}",
                    layer_name=zone_data.get('layer', 'Unknown'),
                    area=self._calculate_area(zone_data.get('points', [])),
                    points=zone_data.get('points', []),
                    bounds=zone_data.get('bounds')
                )
                session.add(zone)
            
            session.commit()
            return str(dwg_file.id)
        finally:
            session.close()
    
    def save_analysis_results(self, project_id: str, analysis_type: str, 
                            parameters: Dict, results: Dict) -> str:
        """Save analysis results"""
        session = self.get_session()
        try:
            analysis = Analysis(
                project_id=project_id,
                analysis_type=analysis_type,
                parameters=parameters,
                results=results,
                total_boxes=results.get('total_boxes', 0),
                efficiency_score=results.get('optimization', {}).get('total_efficiency', 0),
                space_utilization=self._calculate_space_utilization(results)
            )
            session.add(analysis)
            session.flush()
            
            # Save furniture placements
            if 'placements' in results:
                self._save_furniture_placements(session, analysis.id, results['placements'])
            
            session.commit()
            return str(analysis.id)
        finally:
            session.close()
    
    def _save_furniture_placements(self, session, analysis_id: str, placements: Dict):
        """Save furniture placements"""
        for zone_name, zone_placements in placements.items():
            # Get zone by name
            zone = session.query(Zone).filter_by(zone_name=zone_name).first()
            if zone:
                for placement in zone_placements:
                    furniture_placement = FurniturePlacement(
                        zone_id=zone.id,
                        analysis_id=analysis_id,
                        position_x=placement['position'][0],
                        position_y=placement['position'][1],
                        width=placement['size'][0],
                        height=placement['size'][1],
                        suitability_score=placement['suitability_score'],
                        furniture_type='Standard Box'
                    )
                    session.add(furniture_placement)
    
    def save_bim_model(self, project_id: str, bim_model_data: Dict, 
                      compliance_data: Dict) -> str:
        """Save BIM model data"""
        session = self.get_session()
        try:
            bim_model = BIMModel(
                project_id=project_id,
                model_data=bim_model_data,
                ifc_compliance_score=compliance_data.get('ifc', {}).get('score', 0),
                cobie_data=compliance_data.get('cobie', {}),
                standards_compliance=compliance_data
            )
            session.add(bim_model)
            session.commit()
            return str(bim_model.id)
        finally:
            session.close()
    
    def save_furniture_configuration(self, project_id: str, configuration: Dict) -> str:
        """Save furniture configuration"""
        session = self.get_session()
        try:
            furniture_config = FurnitureConfiguration(
                project_id=project_id,
                space_type=configuration.get('space_type', ''),
                total_items=configuration.get('total_items', 0),
                total_cost=configuration.get('total_cost', 0),
                sustainability_score=configuration.get('sustainability_score', 0),
                ergonomic_score=configuration.get('ergonomic_score', 0),
                configuration_data=configuration
            )
            session.add(furniture_config)
            session.commit()
            return str(furniture_config.id)
        finally:
            session.close()
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        session = self.get_session()
        try:
            project = session.query(Project).filter_by(id=project_id).first()
            if project:
                return {
                    'id': str(project.id),
                    'name': project.name,
                    'description': project.description,
                    'created_by': project.created_by,
                    'created_at': project.created_at.isoformat(),
                    'updated_at': project.updated_at.isoformat(),
                    'status': project.status,
                    'project_type': project.project_type,
                    'building_type': project.building_type,
                    'total_area': project.total_area,
                    'floor_count': project.floor_count,
                    'settings': project.settings
                }
            return None
        finally:
            session.close()
    
    def get_user_projects(self, user_id: str) -> List[Dict]:
        """Get all projects for a user"""
        session = self.get_session()
        try:
            projects = session.query(Project).filter_by(created_by=user_id).all()
            return [{
                'id': str(p.id),
                'name': p.name,
                'description': p.description,
                'created_at': p.created_at.isoformat(),
                'status': p.status,
                'project_type': p.project_type,
                'building_type': p.building_type
            } for p in projects]
        finally:
            session.close()
    
    def get_project_analyses(self, project_id: str) -> List[Dict]:
        """Get all analyses for a project"""
        session = self.get_session()
        try:
            analyses = session.query(Analysis).filter_by(project_id=project_id).all()
            return [{
                'id': str(a.id),
                'analysis_type': a.analysis_type,
                'total_boxes': a.total_boxes,
                'efficiency_score': a.efficiency_score,
                'space_utilization': a.space_utilization,
                'created_at': a.created_at.isoformat(),
                'status': a.status
            } for a in analyses]
        finally:
            session.close()
    
    def get_project_zones(self, project_id: str) -> List[Dict]:
        """Get all zones for a project"""
        session = self.get_session()
        try:
            zones = session.query(Zone).join(DWGFile).filter(
                DWGFile.project_id == project_id
            ).all()
            return [{
                'id': str(z.id),
                'zone_name': z.zone_name,
                'layer_name': z.layer_name,
                'area': z.area,
                'points': z.points,
                'room_type': z.room_type,
                'confidence_score': z.confidence_score
            } for z in zones]
        finally:
            session.close()
    
    def add_project_collaborator(self, project_id: str, user_id: str, username: str, 
                               role: str, permissions: List[str]) -> str:
        """Add collaborator to project"""
        session = self.get_session()
        try:
            collaborator = ProjectCollaborator(
                project_id=project_id,
                user_id=user_id,
                username=username,
                role=role,
                permissions=permissions
            )
            session.add(collaborator)
            session.commit()
            return str(collaborator.id)
        finally:
            session.close()
    
    def add_comment(self, project_id: str, user_id: str, username: str, 
                   content: str, x_pos: float = None, y_pos: float = None, 
                   zone_id: str = None) -> str:
        """Add comment to project"""
        session = self.get_session()
        try:
            comment = Comment(
                project_id=project_id,
                user_id=user_id,
                username=username,
                content=content,
                x_position=x_pos,
                y_position=y_pos,
                zone_id=zone_id
            )
            session.add(comment)
            session.commit()
            return str(comment.id)
        finally:
            session.close()
    
    def get_project_comments(self, project_id: str) -> List[Dict]:
        """Get all comments for a project"""
        session = self.get_session()
        try:
            comments = session.query(Comment).filter_by(
                project_id=project_id, resolved=False
            ).order_by(Comment.created_at.desc()).all()
            return [{
                'id': str(c.id),
                'user_id': c.user_id,
                'username': c.username,
                'content': c.content,
                'x_position': c.x_position,
                'y_position': c.y_position,
                'zone_id': str(c.zone_id) if c.zone_id else None,
                'created_at': c.created_at.isoformat()
            } for c in comments]
        finally:
            session.close()
    
    def log_export(self, project_id: str, export_type: str, file_name: str, 
                  file_size: int, created_by: str, settings: Dict = None) -> str:
        """Log export activity"""
        session = self.get_session()
        try:
            export_log = ExportHistory(
                project_id=project_id,
                export_type=export_type,
                file_name=file_name,
                file_size=file_size,
                created_by=created_by,
                export_settings=settings or {}
            )
            session.add(export_log)
            session.commit()
            return str(export_log.id)
        finally:
            session.close()
    
    def get_project_statistics(self, project_id: str) -> Dict:
        """Get comprehensive project statistics"""
        session = self.get_session()
        try:
            # Basic project info
            project = session.query(Project).filter_by(id=project_id).first()
            if not project:
                return {}
            
            # Count analyses
            analysis_count = session.query(Analysis).filter_by(project_id=project_id).count()
            
            # Count zones
            zone_count = session.query(Zone).join(DWGFile).filter(
                DWGFile.project_id == project_id
            ).count()
            
            # Count collaborators
            collaborator_count = session.query(ProjectCollaborator).filter_by(
                project_id=project_id, status='active'
            ).count()
            
            # Count comments
            comment_count = session.query(Comment).filter_by(project_id=project_id).count()
            
            # Get latest analysis
            latest_analysis = session.query(Analysis).filter_by(
                project_id=project_id
            ).order_by(Analysis.created_at.desc()).first()
            
            return {
                'project_name': project.name,
                'total_analyses': analysis_count,
                'total_zones': zone_count,
                'total_collaborators': collaborator_count,
                'total_comments': comment_count,
                'latest_analysis': {
                    'type': latest_analysis.analysis_type if latest_analysis else None,
                    'boxes': latest_analysis.total_boxes if latest_analysis else 0,
                    'efficiency': latest_analysis.efficiency_score if latest_analysis else 0,
                    'date': latest_analysis.created_at.isoformat() if latest_analysis else None
                } if latest_analysis else None,
                'created_at': project.created_at.isoformat(),
                'last_updated': project.updated_at.isoformat()
            }
        finally:
            session.close()
    
    def _calculate_area(self, points: List[List[float]]) -> float:
        """Calculate polygon area using shoelace formula"""
        if len(points) < 3:
            return 0.0
        
        area = 0.0
        n = len(points)
        
        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        
        return abs(area) / 2.0
    
    def _calculate_space_utilization(self, results: Dict) -> float:
        """Calculate space utilization from analysis results"""
        if not results.get('rooms') or not results.get('total_boxes'):
            return 0.0
        
        total_room_area = sum(info['area'] for info in results['rooms'].values())
        box_area = results['total_boxes'] * results['parameters']['box_size'][0] * results['parameters']['box_size'][1]
        
        return (box_area / total_room_area) if total_room_area > 0 else 0.0