from api.base.serializers import (
    IDField,
    LinksField,
    TypeField,
    RelationshipField,
    JSONAPISerializer,
    NodeFileHyperLinkField,
)
from api.base.utils import absolute_reverse
from api.nodes.serializers import NodeStorageProviderSerializer


class DraftNodeSerializer(JSONAPISerializer):
    """
    A very sparse serializer for DraftNodes that will just reveal
    file links for uploading files to the node
    """
    id = IDField(source='_id', read_only=True)
    type = TypeField()

    links = LinksField({
        'self': 'get_absolute_url',
    })

    def get_absolute_url(self, obj):
        kwargs = self.context['request'].parser_context['kwargs']

        return absolute_reverse(
            'draft-nodes:draft-node-detail',
            kwargs=kwargs,
        )

    files = RelationshipField(
        related_view='draft-nodes:node-storage-providers',
        related_view_kwargs={'node_id': '<_id>'},
    )

    class Meta:
        type_ = 'draft-nodes'


class DraftNodeStorageProviderSerializer(NodeStorageProviderSerializer):
    files = NodeFileHyperLinkField(
        related_view='draft-nodes:node-files',
        related_view_kwargs={'node_id': '<node._id>', 'path': '<path>', 'provider': '<provider>'},
        kind='folder',
        never_embed=True,
    )
