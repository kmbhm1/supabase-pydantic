"""Tests for BaseRelationshipMarshaler abstract class."""

import pytest

from supabase_pydantic.db.marshalers.abstract.base_relationship_marshaler import BaseRelationshipMarshaler


class TestBaseRelationshipMarshaler:
    """Tests for BaseRelationshipMarshaler class."""

    def test_base_relationship_marshaler_initialization(self):
        """Test that BaseRelationshipMarshaler can't be instantiated directly."""
        with pytest.raises(TypeError):
            BaseRelationshipMarshaler()

    def test_abstract_determine_relationship_type_method(self):
        """Test that determine_relationship_type abstract method raises NotImplementedError when not overridden."""

        # Create a minimal subclass that doesn't override the abstract methods
        class IncompleteMarshaler(BaseRelationshipMarshaler):
            pass

        # Should raise TypeError when instantiating because abstract methods aren't implemented
        with pytest.raises(TypeError):
            IncompleteMarshaler()

        # Create a minimal implementation that implements only one method
        class PartialMarshaler(BaseRelationshipMarshaler):
            def analyze_table_relationships(self, tables):
                pass

        # Should still raise TypeError since not all abstract methods are implemented
        with pytest.raises(TypeError):
            PartialMarshaler()

    def test_abstract_analyze_table_relationships_method(self):
        """Test that analyze_table_relationships abstract method raises NotImplementedError when not overridden."""

        # Create a minimal implementation that implements only one method
        class PartialMarshaler(BaseRelationshipMarshaler):
            def determine_relationship_type(self, source_table, target_table, source_column, target_column):
                pass

        # Should still raise TypeError since not all abstract methods are implemented
        with pytest.raises(TypeError):
            PartialMarshaler()

    def test_complete_implementation(self):
        """Test that a complete implementation can be instantiated."""

        class CompleteMarshaler(BaseRelationshipMarshaler):
            def determine_relationship_type(self, source_table, target_table, source_column, target_column):
                pass

            def analyze_table_relationships(self, tables):
                pass

        # Should not raise any exception
        marshaler = CompleteMarshaler()
        assert isinstance(marshaler, BaseRelationshipMarshaler)
