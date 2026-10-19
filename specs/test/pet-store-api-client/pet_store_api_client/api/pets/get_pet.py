from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.pet import Pet
from ...types import Response


def _get_kwargs(
    pet_id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/pets/{pet_id}".format(
            pet_id=quote(str(pet_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Pet | None:
    if response.status_code == 200:
        response_200 = Pet.from_dict(response.json())

        return response_200

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | Pet]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pet_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | Pet]:
    """
    Args:
        pet_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Pet]
    """

    kwargs = _get_kwargs(
        pet_id=pet_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pet_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Any | Pet | None:
    """
    Args:
        pet_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Pet
    """

    return sync_detailed(
        pet_id=pet_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    pet_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | Pet]:
    """
    Args:
        pet_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Pet]
    """

    kwargs = _get_kwargs(
        pet_id=pet_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pet_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Any | Pet | None:
    """
    Args:
        pet_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Pet
    """

    return (
        await asyncio_detailed(
            pet_id=pet_id,
            client=client,
        )
    ).parsed
