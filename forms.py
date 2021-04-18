from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, Length

genres_choices = (
    ('Alternative', 'Alternative'), ('Blues', 'Blues'), ('Classical', 'Classical'), ('Country', 'Country'),
    ('Electronic', 'Electronic'), ('Folk', 'Folk'), ('Funk', 'Funk'), ('Hip-Hop', 'Hip-Hop'),
    ('Heavy Metal', 'Heavy Metal'), ('Instrumental', 'Instrumental'), ('Jazz', 'Jazz'),
    ('Musical Theatre', 'Musical Theatre'), ('Pop', 'Pop'), ('Punk', 'Punk'), ('R&B', 'R&B'),
    ('Reggae', 'Reggae'), ('Rock n Roll', 'Rock n Roll'), ('Soul', 'Soul'), ('Other', 'Other'),
)

state_choices = (
    ('AL', 'AL'), ('AK', 'AK'), ('AZ', 'AZ'), ('AR', 'AR'), ('CA', 'CA'), ('CO', 'CO'), ('CT', 'CT'),
    ('DE', 'DE'), ('DC', 'DC'), ('FL', 'FL'), ('GA', 'GA'), ('HI', 'HI'), ('ID', 'ID'), ('IL', 'IL'),
    ('IN', 'IN'), ('IA', 'IA'), ('KS', 'KS'), ('KY', 'KY'), ('LA', 'LA'), ('ME', 'ME'), ('MT', 'MT'),
    ('NE', 'NE'), ('NV', 'NV'), ('NH', 'NH'), ('NJ', 'NJ'), ('NM', 'NM'), ('NY', 'NY'), ('NC', 'NC'),
    ('ND', 'ND'), ('OH', 'OH'), ('OK', 'OK'), ('OR', 'OR'), ('MD', 'MD'), ('MA', 'MA'), ('MI', 'MI'),
    ('MN', 'MN'), ('MS', 'MS'), ('MO', 'MO'), ('PA', 'PA'), ('RI', 'RI'), ('SC', 'SC'), ('SD', 'SD'),
    ('TN', 'TN'), ('TX', 'TX'), ('UT', 'UT'), ('VT', 'VT'), ('VA', 'VA'), ('WA', 'WA'), ('WV', 'WV'),
    ('WI', 'WI'), ('WY', 'WY'),
)


class ShowForm(Form):
    name = StringField(
        'name', validators=[
            DataRequired(),
            Length(max=120),
        ]
    )
    artist_id = SelectField(
        'artist_id',
        # validators=[DataRequired()],
    )
    venue_id = SelectField(
        'venue_id',
        # validators=[DataRequired()],
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )


class VenueForm(Form):
    name = StringField(
        'name', validators=[
            DataRequired(),
            Length(max=120),
        ]
    )
    city = StringField(
        'city', validators=[
            DataRequired(),
            Length(max=120),
        ]
    )
    state = SelectField(
        'state',
        validators=[
            DataRequired(),
            Length(max=120),
            AnyOf([state for state, _ in state_choices]),
        ],
        choices=state_choices
    )
    address = StringField(
        'address',
        validators=[
            DataRequired(),
            Length(max=120),
        ]
    )
    phone = StringField(
        'phone', validators=[
            DataRequired(),
            Length(max=120),
        ],
    )
    image_link = StringField(
        'image_link', validators=[
            # URL(),
            DataRequired(),
            Length(max=500),
        ]
    )
    website = StringField(
        'website', validators=[
            URL(),
            Length(max=120),
        ]
    )
    genres = SelectMultipleField(
        'genres',
        validators=[
            DataRequired(),
            Length(max=120),
        ],
        choices=genres_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[
            URL(),
            DataRequired(),
            Length(max=120),
        ]
    )
    seeking_talent = BooleanField(
        'seeking_talent', validators=[
            AnyOf((True, False)),
        ]
    )
    seeking_description = StringField(
        'seeking_description', validators=[
            Length(max=500),
        ]
    )


class ArtistForm(Form):
    name = StringField(
        'name', validators=[
            DataRequired(),
            Length(max=120),
        ]
    )
    city = StringField(
        'city', validators=[
            DataRequired(),
            Length(max=120),
        ]
    )
    state = SelectField(
        'state',
        validators=[
            DataRequired(),
            Length(max=120),
            AnyOf([state for state, _ in state_choices]),
        ],
        choices=state_choices
    )
    phone = StringField(
        'phone', validators=[
            DataRequired(),
            Length(max=120),
        ],
    )
    genres = SelectMultipleField(
        'genres',
        validators=[
            DataRequired(),
            Length(max=120),
        ],
        choices=genres_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[
            URL(),
            DataRequired(),
            Length(max=120),
        ]
    )
    image_link = StringField(
        'image_link', validators=[
            # URL(),
            DataRequired(),
            Length(max=500),
        ]
    )
    website = StringField(
        'website', validators=[
            URL(),
            Length(max=120),
        ]
    )
    seeking_venue = BooleanField(
        'seeking_venue', validators=[
            AnyOf((True, False)),
        ]
    )
    seeking_description = StringField(
        'seeking_description', validators=[
            Length(max=500),
        ]
    )
