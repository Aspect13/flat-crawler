import {Link} from "@mui/material";
import {districtsMap} from "./constants.js";

export const gridColumns = [
    {
		field: 'id', headerName: 'id'
    },
    {
		field: 'district',
        headerName: 'Район',
        width: 120,
        type: 'singleSelect',
        valueOptions: districtsMap,
    },
    {
		field: 'address',
        headerName: 'Адрес',
        flex: true,
        minWidth: 150
    },
    {
		field: 'rooms',
        headerName: 'Комнат',
        type: 'number'
    },
    {
		field: 'area',
        headerName: 'Площадь',
        valueFormatter: (value) => value && `${value} m²`,
        type: 'number'
    },
    {
		field: 'floor',
        headerName: 'Этаж',
        type: 'number'
    },
    {
		field: 'floors',
        headerName: 'Этажей в доме',
        type: 'number'
    },
    {
		field: 'price',
        headerName: 'Цена',
        valueFormatter: (value) => value && `$${value}`,
        type: 'number'
    },
    {
        field: 'location',
        headerName: 'Location',
        renderCell: (params) => <Link href={params.value} target={'_blank'}>{params.value}</Link>
    },
    {
		field: 'link_to_post',
        headerName: 'Ссылка на пост ТГ',
        renderCell: (params) => <Link href={params.value} target={'_blank'}>{params.value}</Link>,
        width: 170
    },
    {
		field: 'created_at',
        headerName: 'Posted at',
        type: 'dateTime',
        valueFormatter: (value) => value && new Date(value.trim('Z') + 'Z').toLocaleString(),
        width: 160
    },
    {
        field: 'added_to_db', 
        headerName: 'Added here',
        type: 'dateTime',
        valueFormatter: (value) => value && new Date(value.trim('Z') + 'Z').toLocaleString(),
        width: 160
    }
]

